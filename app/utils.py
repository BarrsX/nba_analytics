def draw_court(fig, line_color="white", line_width=2):
    """
    Returns a figure with basketball court lines
    """
    # Court dimensions (in feet, NBA coordinate system)
    court_width = 50
    key_width = 16
    backboard_width = 6
    rim_radius = 0.75
    three_point_radius = 23.75
    three_point_side_radius = 22
    key_height = 19
    free_throw_circle_radius = 6
    restricted_circle_radius = 4

    # Draw the three point arc
    fig.add_shape(
        type="path",
        path=f"M {-three_point_side_radius} 0 L {-three_point_side_radius} {14} A {three_point_radius} {three_point_radius} 0 1 1 {three_point_side_radius} {14} L {three_point_side_radius} 0",
        line=dict(color=line_color, width=line_width),
        layer="below",
    )

    # Draw key box
    fig.add_shape(
        type="rect",
        x0=-key_width / 2,
        y0=0,
        x1=key_width / 2,
        y1=key_height,
        line=dict(color=line_color, width=line_width),
        layer="below",
    )

    # Draw free throw circle
    fig.add_shape(
        type="circle",
        x0=-free_throw_circle_radius,
        y0=key_height - free_throw_circle_radius,
        x1=free_throw_circle_radius,
        y1=key_height + free_throw_circle_radius,
        line=dict(color=line_color, width=line_width),
        layer="below",
    )

    # Draw restricted area
    fig.add_shape(
        type="circle",
        x0=-restricted_circle_radius,
        y0=-restricted_circle_radius,
        x1=restricted_circle_radius,
        y1=restricted_circle_radius,
        line=dict(color=line_color, width=line_width),
        layer="below",
    )

    # Draw backboard
    fig.add_shape(
        type="line",
        x0=-backboard_width / 2,
        y0=4,
        x1=backboard_width / 2,
        y1=4,
        line=dict(color=line_color, width=line_width),
        layer="below",
    )

    # Draw rim
    fig.add_shape(
        type="circle",
        x0=-rim_radius,
        y0=-rim_radius,
        x1=rim_radius,
        y1=rim_radius,
        line=dict(color=line_color, width=line_width),
        layer="below",
    )

    return fig
