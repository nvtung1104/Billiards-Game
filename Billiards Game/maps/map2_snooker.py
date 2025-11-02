def create_snooker_map():
    """
    Trả về cấu hình cho bàn Snooker.
    - width,height: kích thước bàn (game sẽ đặt Table.x/y dựa trên kích thước màn)
    - pockets: list các vị trí tương đối (rx,ry) trong [0..1] theo table width/height
    - balls: danh sách quả bi với tọa độ tương đối (rx,ry), number, color, is_cue
    - scoring: function(ball_number) -> points
    """
    cfg = {}
    cfg['width'] = 760
    cfg['height'] = 460
    # pockets: 6 lỗ (4 góc + 2 giữa cạnh trên/dưới)
    cfg['pockets'] = [
        (0.0, 0.0),   # top-left
        (1.0, 0.0),   # top-right
        (0.0, 1.0),   # bottom-left
        (1.0, 1.0),   # bottom-right
        (0.5, 0.0),   # top-middle
        (0.5, 1.0)    # bottom-middle
    ]
    balls = []
    # cue ball
    balls.append({'rx': 0.20, 'ry': 0.50, 'number': 0, 'color': (255,255,255), 'is_cue': True})
    # 15 red balls (number 1) in triangle near far end
    base_x = 0.72
    base_y = 0.50
    offset = 2 * 15 / 100.0  # scaled minor offset
    num = 1
    # triangle packing approx
    rows = 5
    for r in range(rows):
        for c in range(r+1):
            rx = base_x + r * 0.025
            ry = base_y + (c - r/2) * (0.035)
            balls.append({'rx': rx, 'ry': ry, 'number': 1, 'color': (180, 20, 20), 'is_cue': False})
            num += 1
    # 6 colors: yellow, green, brown, blue, pink, black with points 2..7
    color_defs = [
        (2, (255, 235, 59), 0.35, 0.18),  # yellow
        (3, (76, 175, 80), 0.42, 0.18),   # green
        (4, (150, 75, 0), 0.49, 0.18),    # brown
        (5, (33, 150, 243), 0.61, 0.30),  # blue (center)
        (6, (219, 64, 119), 0.66, 0.40),  # pink (near reds)
        (7, (20, 20, 20), 0.74, 0.10)     # black (deep)
    ]
    for num, col, rx, ry in color_defs:
        balls.append({'rx': rx, 'ry': ry, 'number': num, 'color': col, 'is_cue': False})

    cfg['balls'] = balls

    def scoring(number):
        # snooker: red=1, yellow=2,...black=7, cue=0 -> no points
        if number == 0:
            return 0
        # reds were placed with number==1 already
        return int(number)  # treat ball.number as snooker points

    cfg['scoring'] = scoring
    cfg['mode'] = 'snooker'
    return cfg