def create_carom_map(mode='libre'):
    """
    Trả về cấu hình cho bàn Carom (không lỗ, 3 bi).
    mode: 'libre' | 'one' | 'three'  (libre: chỉ cần chạm 2 bi; one: 1 băng; three: 3 băng)
    """
    cfg = {}
    # Carom thường là bàn lớn, nhưng giữ trong giới hạn màn
    cfg['width'] = 760
    cfg['height'] = 460
    # no pockets
    cfg['pockets'] = []
    # balls: cue (white), opponent (yellow), red
    balls = []
    balls.append({'rx': 0.20, 'ry': 0.50, 'number': 0, 'color': (255,255,255), 'is_cue': True})
    balls.append({'rx': 0.75, 'ry': 0.40, 'number': 2, 'color': (255, 215, 0), 'is_cue': False})  # yellow
    balls.append({'rx': 0.75, 'ry': 0.60, 'number': 1, 'color': (200, 30, 30), 'is_cue': False})  # red (target)
    cfg['balls'] = balls

    # scoring for carom: success -> fixed points
    def scoring(number):
        # no pocketing; scoring happens on successful carom
        return 0

    cfg['scoring'] = scoring
    cfg['mode'] = mode  # 'libre', 'one', 'three'
    return cfg