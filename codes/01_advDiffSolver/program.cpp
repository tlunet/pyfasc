#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cassert>
#include <cmath>
#include <chrono>

using std::vector, std::istream, std::string, std::ifstream, std::ofstream;
using std::cout, std::endl;

class Array2D {

public:
    static const int nHalo = 2;
    const int nX, nY;
    const int nXH, nYH;
    
    const int size;
protected:
    vector<double> data;
    inline int idx(int x, int y) const { return (x+nHalo) + (y+nHalo)*nXH; }
    inline void checkShape(const Array2D& other) { assert((this->nX == other.nX) and (this->nY == other.nY)); }

public:
    Array2D(int nX, int nY): 
        nX(nX), nY(nY), nXH(nX+2*nHalo), nYH(nY+2*nHalo),
        size(nXH*nYH), data(size) {}
    
    Array2D(const Array2D& other):
        nX(other.nX), nY(other.nY), nXH(other.nXH), nYH(other.nYH),
        size(other.size), data(other.data) {}
        
    inline Array2D& operator=(const Array2D& other) { 
        if (this != &other) {
            checkShape(other);
            for (int y = 0; y < nY; y++)
            for (int x = 0; x < nX; x++) {
                this->value(x,y) = other.value(x,y);
            }
        }
        return *this;
    }

    inline Array2D& operator+=(const Array2D& other) {
        checkShape(other);
        for (int y = 0; y < nY; y++)
        for (int x = 0; x < nX; x++) {
            this->value(x,y) += other.value(x,y);
        }
        return *this;
    }

    inline Array2D& operator*=(const double& factor) {
        for (int y = 0; y < nY; y++)
        for (int x = 0; x < nX; x++) {
            this->value(x,y) *= factor;
        }
        return *this;
    }

    inline void aypx(const double& factor, const Array2D& other) {
        checkShape(other);
        for (int y = 0; y < nY; y++)
        for (int x = 0; x < nX; x++) {
            this->value(x,y) = factor*this->value(x,y) + other.value(x,y);
        }
    }

    inline void axpy(const double& factor, const Array2D& other) {
        checkShape(other);
        for (int y = 0; y < nY; y++)
        for (int x = 0; x < nX; x++) {
            this->value(x,y) = this->value(x,y) + factor*other.value(x,y);
        }
    }
    
    inline const double& value(int x, int y) const { return data.at(idx(x, y)); }
    inline double& value(int x, int y) { return data.at(idx(x, y)); }

    void setup(istream& in) {
        string initType; in >> initType;
        double dX = 1./nX, dY = 1./nY;

        if (initType == "gauss") {
            for (int y = 0; y < nY; y++)
            for (int x = 0; x < nX; x++) {
                value(x, y) = std::exp(-200*(std::pow(x*dX-0.25, 2) + std::pow(y*dY-0.25, 2)));
            }

        } else if (initType == "sinus") {
            for (int y = 0; y < nY; y++)
            for (int x = 0; x < nX; x++) {
                value(x, y) = std::sin(2*M_PI*x*dX)*std::sin(2*M_PI*y*dY);
            }

        } else if (initType == "cross") {
            for (int y = 0; y < nY; y++)
            for (int x = 0; x < nX; x++) {
                double xVal = x*dX, yVal = y*dY;
                value(x, y) = 0.5*(
                    std::exp(-200*(xVal-0.5)*(xVal-0.5)) + std::exp(-200*(yVal-0.5)*(yVal-0.5))
                );
            }

        } else if (initType == "cross2") {
            for (int y = 0; y < nY; y++)
            for (int x = 0; x < nX; x++) {
                double xVal = x*dX, yVal = y*dY;
                double eX = std::exp(-200*(xVal-0.5)*(xVal-0.5)), eY = std::exp(-200*(yVal-0.5)*(yVal-0.5));
                value(x, y) = std::max(eX, eY);
            }

        } else {
            throw "unknown initType";
        }
    }

    void write(const string& fileName) {
        ofstream output(fileName);
        for (int y = 0; y < nY; y++) {
            for (int x = 0; x < nX; x++) {
                output << value(x, y) << " ";
            }
            output << "\n";
        }
    }

    void updateHalo() {
        for (int x=0; x<nX; x++)
        for (int s: {1, 2}) {
            value(x, -s) = value(x, nY-s);
            value(x, nY+(s-1)) = value(x, s-1);
        }
        for (int y=0; y<nY; y++)
        for (int s: {1, 2}) {
            value(-s, y) = value(nX-s, y);
            value(nX+(s-1), y) = value(s-1, y);
        }
    }

};

class Coeffs2D {
    static constexpr int nHalo = 2;

    vector<double> data;
    const int nX, nY;
    const int xChunk, yChunk, cChunk;

    inline int idx(int s, int x, int y) const { return (s+nHalo) + x*xChunk + y*yChunk; }

public:
    Coeffs2D(int nX, int nY): 
        data(2*(2*nHalo+1)*nX*nY), nX(nX), nY(nY),
        xChunk((2*nHalo+1)), yChunk((2*nHalo+1)*nX), cChunk((2*nHalo+1)*nX*nY) {}

    inline const double& valX(int s, int x, int y) const { return data.at(idx(s, x, y)); }
    inline double& valX(int s, int x, int y) { return data.at(idx(s, x, y)); }

    inline const double& valY(int s, int x, int y) const { return data.at(idx(s, x, y) + cChunk); }
    inline double& valY(int s, int x, int y) { return data.at(idx(s, x, y) + cChunk); }

    void setup(istream& in) {
        string flowType; double viscosity; in >> flowType >> viscosity;

        double dX = 1./nX, dY = 1./nY;
        double dX2 = dX*dX, dY2 = dY*dY;
        vector<double> cAdv = { 1./12, -2./3,  0,    2./3, -1./12};
        vector<double> cDif = {-1./12,  4./3, -5./2, 4./3, -1./12};

        if (flowType == "diagonal") {
            for (int y = 0; y < nY; y++)
            for (int x = 0; x < nX; x++) 
            for (int s = -nHalo; s < nHalo+1; s++) {
                valX(s, x, y) = -cAdv[s+nHalo]/dX + viscosity*cDif[s+nHalo]/dX2;
                valY(s, x, y) = -cAdv[s+nHalo]/dY + viscosity*cDif[s+nHalo]/dY2;
            }

        } else if (flowType == "circular") {
            for (int y = 0; y < nY; y++)
            for (int x = 0; x < nX; x++) {
                
                double r = std::hypot(x*dX-0.5, y*dY-0.5);
                double phi = std::atan2(y*dY-0.5, x*dX-0.5);
                double rho = std::exp(-10*r*r);
                double vX = -r*2*M_PI*std::sin(phi)*rho;
                double vY =  r*2*M_PI*std::cos(phi)*rho;

                for (int s = -nHalo; s < nHalo+1; s++) {
                    valX(s, x, y) = -vX*cAdv[s+nHalo]/dX + viscosity*cDif[s+nHalo]/dX2;
                    valY(s, x, y) = -vY*cAdv[s+nHalo]/dY + viscosity*cDif[s+nHalo]/dY2;
                } 
            }

        } else if (flowType == "circular2") {
            for (int y = 0; y < nY; y++)
            for (int x = 0; x < nX; x++) {
                
                double r = std::hypot(x*dX-0.5, y*dY-0.5);
                double phi = std::atan2(y*dY-0.5, x*dX-0.5);
                double rho = std::exp(-5*r*r);
                double vX = -r*2*M_PI*std::sin(phi)*std::sin(4*M_PI*r)*rho;
                double vY =  r*2*M_PI*std::cos(phi)*std::sin(4*M_PI*r)*rho;

                for (int s = -nHalo; s < nHalo+1; s++) {
                    valX(s, x, y) = -vX*cAdv[s+nHalo]/dX + viscosity*cDif[s+nHalo]/dX2;
                    valY(s, x, y) = -vY*cAdv[s+nHalo]/dY + viscosity*cDif[s+nHalo]/dY2;
                } 
            }
            
        } else {
            throw "unknown flowType";
        }
    }
};

class Problem {
    Array2D* u, *uEval, *u1, *k;
    Coeffs2D* coeffs;

    double t = 0;
    int nSteps;
    double tEnd;

public:

    void setup(istream& in) {
        int nX, nY; in >> nX >> nY;

        u = new Array2D(nX, nY);
        coeffs = new Coeffs2D(nX, nY);

        u->setup(in);
        coeffs->setup(in);

        in >> tEnd >> nSteps;
    }

    virtual ~Problem() {
        delete u;
        delete coeffs;
    }

private:
    const Array2D& computeRHS(Array2D& uEval, const double&, Array2D& out) {
        assert((out.nX == uEval.nX) and (out.nY == uEval.nY));
        uEval.updateHalo();
    
        for (int y = 0; y < uEval.nY; y++)
        for (int x = 0; x < uEval.nX; x++) {
            out.value(x, y) = 0;
            for (int s = -2; s < 3; s++) {
                out.value(x, y) += coeffs->valX(s, x, y) * uEval.value(x+s, y) 
                                 + coeffs->valY(s, x, y) * uEval.value(x, y+s);
            }
        }
        return out;
    }

public:
    void simulate() {
        Array2D u0 (*this->u);
        Array2D uEval(u0.nX, u0.nY);

        Array2D u1(u0);
        Array2D k(u0.nX, u0.nY);

        double dt = tEnd/nSteps;

        auto tBeg = std::chrono::high_resolution_clock::now();
        // Loop over all time-steps
        for (int i = 0; i < nSteps; i++) {

            // First stage
            uEval = computeRHS(u0, t, k);
            k *= dt/6; u1 += k;

            // Second stage
            uEval *= dt/2; uEval += u0;
            uEval = computeRHS(uEval, t+dt/2, k);
            k *= dt/3; u1 += k;

            // Third stage
            uEval *= dt/2; uEval += u0;
            uEval = computeRHS(uEval, t+dt/2, k);
            k *= dt/3; u1 += k;

            // Fourth stage
            uEval *= dt; uEval += u0;
            computeRHS(uEval, t+dt, k); 
            k *= dt/6; u1 += k;

            // Save result
            u0 = u1;
            t = (i+1)*dt;
        }
        auto tEnd = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> duration = tEnd-tBeg;
        std::cout << "tWall : " << duration.count() << " seconds" << std::endl;
        auto tScaled = duration.count()/(nSteps * u->nX * u->nY);
        std::cout << "tWall/DoF : " << tScaled << " seconds" << std::endl;
    }

    void simulate_B() {
        Array2D& u0 = *this->u;
        Array2D uEval(u0.nX, u0.nY);

        Array2D u1(u0);
        Array2D k(u0.nX, u0.nY);

        double dt = tEnd/nSteps;

        auto tBeg = std::chrono::high_resolution_clock::now();
        // Loop over all time-steps
        for (int i = 0; i < nSteps; i++) {

            // First stage
            uEval = computeRHS(u0, t, k);
            u1.axpy(dt/6, k);

            // Second stage
            uEval.aypx(dt/2, u0);
            uEval = computeRHS(uEval, t+dt/2, k);
            u1.axpy(dt/3, k);

            // Third stage
            uEval.aypx(dt/2, u0);
            uEval = computeRHS(uEval, t+dt/2, k);
            u1.axpy(dt/3, k);

            // Fourth stage
            uEval.aypx(dt, u0);
            computeRHS(uEval, t+dt, k); 
            u1.axpy(dt/6, k);

            // Save result
            u0 = u1;
            t = (i+1)*dt;
        }
        auto tEnd = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> duration = tEnd-tBeg;
        std::cout << "tWall : " << duration.count() << " seconds" << std::endl;
    } 

    void writeSolution(const string& fileName) { u->write(fileName); }

};


int main() {
    ifstream input("input.txt");
    if (not input) {
        cout << "Error : missing input.txt file" << endl;
        return 1;
    }

    Problem p;
    p.setup(input);
    p.writeSolution("uInit.txt");

    p.simulate();
    p.writeSolution("uEnd.txt");
}