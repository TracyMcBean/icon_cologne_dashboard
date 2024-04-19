

def style_figure(fig):
    """ This function styles the figure by setting the font color to white and the background to transparent.
    """
    fig.update_layout(
        font=dict(
            color="white"
        ),
        plot_bgcolor='#d3e4ed',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig