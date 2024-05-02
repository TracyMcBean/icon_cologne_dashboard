

def style_figure(fig):
    """ This function styles the figure by setting the font color to white and
      the background to transparent.

    :param fig: The figure to be updated
    :return: The updated figure
    """
    fig.update_layout(
        font=dict(
            color="white"
        ),
        plot_bgcolor='#d3e4ed',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig

def style_error(fig):
    """ This function will update the figure if an error occurs.

    :param fig: The figure to be updated
    :return: The updated figure
    """

    fig.update_layout(
        font=dict(
            color="white"
        ),
        plot_bgcolor='#d3e4ed',
        paper_bgcolor='rgba(0,0,0,0)',
        title='Error when reading data',
        title_x=0.5,
        title_y=0.5,
        title_font=dict(size=24),
    )
    return fig