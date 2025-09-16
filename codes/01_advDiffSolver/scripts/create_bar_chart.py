import plotly.graph_objects as go


def create_bar_chart(results):
    """Create interactive bar chart for runtime comparison"""
    if not results or 'test_cases' not in results:
        return None
    
    test_cases = results['test_cases']
    lang1 = results['languages']['program1']
    lang2 = results['languages']['program2']
    
    # Prepare data
    case_names = []
    prog1_times = []
    prog2_times = []
    
    for i, (case_name, case_data) in enumerate(test_cases.items()):
        case_names.append(case_name)
        prog1_times.append(case_data['program1']['runtime'])
        prog2_times.append(case_data['program2']['runtime'])
    
    # Create Bar Chart for runtime comparison
    bar_fig = go.Figure()
    
    bar_fig.add_trace(
        go.Bar(name=f'Program 1 ({lang1})', x=case_names, y=prog1_times, marker_color='lightblue')
    )
    bar_fig.add_trace(
        go.Bar(name=f'Program 2 ({lang2})', x=case_names, y=prog2_times, marker_color='lightcoral')
    )
    
    bar_fig.update_xaxes(title_text="Test Cases")
    bar_fig.update_yaxes(title_text="Runtime (seconds)")
    
    bar_fig.update_layout(
        title=f"Runtime Comparison: {lang1.title()} vs {lang2.title()}",
        height=500,
        showlegend=True
    )
    
    return bar_fig
