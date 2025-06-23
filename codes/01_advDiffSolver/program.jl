## import
#using LinearAlgebra
using BenchmarkTools
using Plots; gr()

## define
@Base.kwdef mutable struct adv_diff_parameters
    # Inputs from file with defaults
    nX        :: Int                = 256 
    nY        :: Int                = 256
    initType  :: String             = "cross2"
    flowType  :: String             = "circular2"
    viscosity :: Float64            = 0.0
    tEnd      :: Float64            = 0.125
    nSteps    :: Int                = 125
    # Other
    dlo       :: Tuple{Int, Int}    = (nHalo+1, nHalo+1)
    dhi       :: Tuple{Int, Int}    = (nHalo+nX, nHalo+nY)
    ndof      :: Tuple{Int, Int}    = (2*nHalo+nX, 2*nHalo+nY)
end # struct adv_diff_parameters

function read_inputs_and_update_parameters!(filename::String,parms::adv_diff_parameters)
    f = open(filename, "r")
    lines = readlines(f)
    parms.nX, parms.nY = parse.(Int,split(lines[1]))
    line = split(lines[2])
    parms.initType, parms.flowType = line[1:2]
    parms.viscosity = parse(Float64, line[3])
    line = split(lines[3])
    parms.tEnd = parse(Float64,line[1])
    parms.nSteps = parse(Int,line[2])
    # update derived parameters
    parms.dlo = (nHalo+1, nHalo+1)
    parms.dhi = (nHalo+parms.nX, nHalo+parms.nY)
    parms.ndof = (2*nHalo+parms.nX, 2*nHalo+parms.nY)
    # close file
    close(f)
end # read_inputs_and_update_parameters!

function updateHalo!(u::Matrix{Float64})
    nH2 = 2*nHalo
    u[1:nHalo,         nHalo+1:end-nHalo] = u[end-nH2+1:end-nHalo, nHalo+1:end-nHalo]
    u[end-nHalo+1:end, nHalo+1:end-nHalo] = u[nHalo+1:nH2,         nHalo+1:end-nHalo]
    u[nHalo+1:end-nHalo,         1:nHalo] = u[nHalo+1:end-nHalo, end-nH2+1:end-nHalo]
    u[nHalo+1:end-nHalo, end-nHalo+1:end] = u[nHalo+1:end-nHalo,         nHalo+1:nH2] 
end # updateHalo!

function generate_grid(parms::adv_diff_parameters)
    Δx, Δy = 1.0/parms.nX, 1.0/parms.nY
    x = [(ii-0.5)*Δx for ii = 1:parms.nX]
    y = [(ii-0.5)*Δy for ii = 1:parms.nY]
    return x, y
end # generate_grid

function updateHalo!(u::Matrix{Float64})
    nH2 = 2*nHalo
    u[1:nHalo,         nHalo+1:end-nHalo] = u[end-nH2+1:end-nHalo, nHalo+1:end-nHalo]
    u[end-nHalo+1:end, nHalo+1:end-nHalo] = u[nHalo+1:nH2,         nHalo+1:end-nHalo]
    u[nHalo+1:end-nHalo,         1:nHalo] = u[nHalo+1:end-nHalo, end-nH2+1:end-nHalo]
    u[nHalo+1:end-nHalo, end-nHalo+1:end] = u[nHalo+1:end-nHalo,         nHalo+1:nH2] 
end # updateHalo!

function generate_initial_condition(parms::adv_diff_parameters, x::Vector{Float64}, y::Vector{Float64})
    # init
    init_sol = zeros(parms.ndof[1], parms.ndof[2])
    yT = transpose(y)
    # define
    if parms.initType == "gauss"
        init_sol[parms.dlo[1]:parms.dhi[1], parms.dlo[2]:parms.dhi[2]] = exp.(-200.0 .* ((x .- 0.25).^2 .+ (yT .- 0.25).^2))
    elseif  parms.initType == "square"
        init_sol[parms.dlo[1]:parms.dhi[1], parms.dlo[2]:parms.dhi[2]] = float.((x .> 0.2).*(x .< 0.3).*(yT .> 0.2).*(yT .< 0.3))
    elseif parms.initType == "cross"
        init_sol[parms.dlo[1]:parms.dhi[1], parms.dlo[2]:parms.dhi[2]] = 0.5 .* ( exp.(-200.0 .* (x .- 0.5).^2) .+ exp.(-200.0 .* (yT .- 0.5).^2))
    elseif parms.initType == "cross2"
        init_sol[parms.dlo[1]:parms.dhi[1], parms.dlo[2]:parms.dhi[2]] = max.(exp.(-200.0 .* (x .- 0.5).^2), exp.(-200.0 .* (yT .- 0.5).^2))
    else
        @error("unknown initType : $(parms.initType)")
    end
    #
    return init_sol
end # generate_initial_condition

function setup_coeffs(parms::adv_diff_parameters, x::Vector{Float64}, y::Vector{Float64})
    # allocate
    coeffs = zeros(parms.nX, parms.nY, 2*nHalo+1, 2)
    Δx, Δy = 1.0/parms.nX, 1.0/parms.nY
    yT = transpose(y)
    vX, vY = zeros(parms.nX, parms.nY), zeros(parms.nX, parms.nY)
    # hardcoded parameters
    cAdv = [ 1.0/12, -2.0/3,    0.0, 2.0/3, -1.0/12]    # dim (nHalo*2+1)    
    cDif = [-1.0/12,  4.0/3, -5.0/2, 4.0/3, -1.0/12]    # dim (nHalo*2+1)
    # compute
    if parms.flowType == "diagonal"
            vX .= 1.0
            vY .= 1.0
    elseif parms.flowType == "circular"
        r = sqrt.( (x .- 0.5).^2 .+ (yT .- 0.5).^2 )
        phi= atan.(yT.-0.5, x .- 0.5)
        rho = exp.(-10.0 .* r.^2)
        vX = -r .* 2.0 .* π .* sin.(phi) .* rho
        vY =  r .* 2.0 .* π .* cos.(phi) .* rho
    elseif parms.flowType == "circular2"
        r = sqrt.( (x .- 0.5).^2 .+ (yT .- 0.5).^2 )
        phi= atan.(yT.-0.5, x .- 0.5)
        rho = exp.(-5.0 .* r.^2)
        vX = -r .* 2.0 .* π .* sin.(phi) .* sin.(4.0 * π .* r) .* rho
        vY =  r .* 2.0 .* π .* cos.(phi) .* sin.(4.0 * π .* r) .* rho
    else
        @warn("unknown flowType: $(parms.flowType), using vX, vY = 0.0")
        # do nothng already initialized to zero
    end
    coeffs[:, :, :, 1] = (-vX .* reshape(cAdv,(1,1,5))./Δx) .+ (parms.viscosity .* reshape(cDif,(1,1,5))./Δx).^2
    coeffs[:, :, :, 2] = (-vY .* reshape(cAdv,(1,1,5))./Δy) .+ (parms.viscosity .* reshape(cDif,(1,1,5))./Δy).^2
    #
    return coeffs
end # setup_coeffs

function update_RHS_and_boundary!(sol::Matrix{Float64}, RHS::Matrix{Float64}, coeffs::Array{Float64,4}, parms::adv_diff_parameters)
    # allocate
    nX, nY = parms.nX,parms.nY
    t = zeros(nX,nY)
    updateHalo!(sol)
    RHS .= 0.0
    #
    for ii in axes(coeffs, 3)
        # Derivative in X
        copyto!(t, CartesianIndices(t), sol, CartesianIndices((ii:nX+ii-1, parms.dlo[2]:parms.dhi[2])))
        t .*= coeffs[:, :, ii, 1]
        RHS += t

        # Derivative in Y
        copyto!(t, CartesianIndices(t), sol, CartesianIndices((parms.dlo[1]:parms.dhi[1], ii:nY+ii-1)))
        t .*= coeffs[:, :, ii, 2]
        RHS += t
    end
end # compute_RHS

function simulate_adv_diff(parms::adv_diff_parameters, u0::Matrix{Float64}, coeffs::Array{Float64,4})
    # allocate
    uEval = zeros(size(u0))
    u1 = zeros(parms.nX, parms.nY)
    copyto!(u1, CartesianIndices(u1), u0, CartesianIndices((parms.dlo[1]:parms.dhi[1], parms.dlo[2]:parms.dhi[2])))
    RHS = zeros(parms.nX, parms.nY)
    # time step
    Δt = parms.tEnd / parms.nSteps
    @btime simulation_loop($parms, $u0, $RHS, $uEval, $u1, $coeffs, $Δt) 
    #simulation_loop(parms, u0, RHS, uEval, u1, coeffs, Δt) 
    return u0
end # simulate_adv_diff

function simulation_loop(parms::adv_diff_parameters, u0::Matrix{Float64}, RHS::Matrix{Float64}, uEval::Matrix{Float64}, u1::Matrix{Float64}, coeffs::Array{Float64,4}, Δt::Float64)
    # just extra function for @btime
    for ti in 1:parms.nSteps    
        
        update_RHS_and_boundary!(u0, RHS, coeffs, parms)
        copyto!(uEval, CartesianIndices((parms.dlo[1]:parms.dhi[1], parms.dlo[2]:parms.dhi[2])), RHS, CartesianIndices((RHS)))
        RHS .*= Δt/6
        u1 .+= RHS
        
        
        uEval .*= Δt/2
        uEval .+= u0
        update_RHS_and_boundary!(uEval, RHS, coeffs, parms)
        copyto!(uEval, CartesianIndices((parms.dlo[1]:parms.dhi[1], parms.dlo[2]:parms.dhi[2])), RHS, CartesianIndices((RHS)))
        RHS .*= Δt/3
        u1 .+= RHS

        
        uEval .*= Δt/2
        uEval .+= u0
        update_RHS_and_boundary!(uEval, RHS, coeffs, parms)
        copyto!(uEval, CartesianIndices((parms.dlo[1]:parms.dhi[1], parms.dlo[2]:parms.dhi[2])), RHS, CartesianIndices((RHS)))
        RHS .*= Δt/3
        u1 .+= RHS

        
        uEval .*= Δt
        uEval .+= u0
        update_RHS_and_boundary!(uEval, RHS, coeffs, parms)
        copyto!(uEval, CartesianIndices((parms.dlo[1]:parms.dhi[1], parms.dlo[2]:parms.dhi[2])), RHS, CartesianIndices((RHS)))
        RHS .*= Δt/6
        u1 .+= RHS

        
        copyto!(u0, CartesianIndices((parms.dlo[1]:parms.dhi[1], parms.dlo[2]:parms.dhi[2])), u1, CartesianIndices((u1)))
        
    end
end # simulation_loop


## Parameters
const nHalo = 2
filename = "codes/01_advDiffSolver/input.txt"

# get parameters
parms = adv_diff_parameters()
read_inputs_and_update_parameters!(filename, parms)

# initialize
xvec, yvec = generate_grid(parms)
u0 = generate_initial_condition(parms, xvec, yvec)
coeffs = setup_coeffs(parms, xvec, yvec)

# run simulation
simulate_adv_diff(parms, u0, coeffs)

# plot
fig = plot()
contourf!(fig, xvec, yvec, u0[parms.dlo[1]:parms.dhi[1], parms.dlo[2]:parms.dhi[2]], color=:viridis, levels=20, aspect_ratio=:equal, size=(600,600))
plot!(fig,xticks=0:0.2:1, yticks=0:0.2:1, xlabel="x", ylabel="y", title = "$(parms.flowType) + $(parms.initType)", label="")
