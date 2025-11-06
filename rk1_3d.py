from PIL import Image, ImageDraw
import math


def bresenham_line(x0, y0, x1, y1):
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = 1 if x1 > x0 else -1
    sy = 1 if y1 > y0 else -1

    if dx > dy:
        err = dx / 2.0
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy

    points.append((x, y))
    return points


def bresenham_circle_full(x0, y0, radius):
    points = []
    x = 0
    y = radius
    d = 3 - 2 * radius

    while x <= y:
        # Добавляем все 8 симметричных точек
        points.extend([
            (x0 + x, y0 + y), (x0 + y, y0 + x),
            (x0 - x, y0 + y), (x0 - y, y0 + x),
            (x0 - x, y0 - y), (x0 - y, y0 - x),
            (x0 + x, y0 - y), (x0 + y, y0 - x)
        ])

        if d < 0:
            d = d + 4 * x + 6
        else:
            d = d + 4 * (x - y) + 10
            y -= 1
        x += 1

    # Удаляем дубликаты
    unique_points = []
    for point in points:
        if point not in unique_points:
            unique_points.append(point)

    return unique_points


def bresenham_arc(x0, y0, radius, start_angle, end_angle):
    # Получаем все точки полной окружности
    circle_points = bresenham_circle_full(x0, y0, radius)

    # Фильтруем точки, которые попадают в заданный угол
    arc_points = []
    for x, y in circle_points:
        # Вычисляем угол точки относительно центра
        dx = x - x0
        dy = y - y0
        angle = math.degrees(math.atan2(dy, dx))
        if angle < 0:
            angle += 360

        # Проверяем, попадает ли точка в заданный диапазон углов
        if start_angle <= angle <= end_angle:
            arc_points.append((x, y))

    return arc_points


def draw_solid_line_bresenham(draw, x0, y0, x1, y1, color='gray', width=1):
    # Получаем все точки линии
    line_points = bresenham_line(x0, y0, x1, y1)

    # Рисуем точки линии с заданной толщиной
    for x, y in line_points:
        for dx in range(-width // 2, width // 2 + 1):
            for dy in range(-width // 2, width // 2 + 1):
                if dx * dx + dy * dy <= (width / 2) ** 2:
                    draw.point((x + dx, y + dy), fill=color)


def draw_dashed_line_bresenham(draw, x0, y0, x1, y1, dash_count=6, color='red', width=1):
    # Получаем все точки линии
    line_points = bresenham_line(x0, y0, x1, y1)

    # Вычисляем длину сегментов
    total_length = len(line_points)
    segment_length = total_length / (2 * dash_count)  # 2 * dash_count потому что чередуем штрихи и пропуски

    # Рисуем штрихи
    for i in range(dash_count):
        start_idx = int(2 * i * segment_length)
        end_idx = int((2 * i + 1) * segment_length)

        # Рисуем точки в сегменте
        for j in range(start_idx, min(end_idx, len(line_points))):
            x, y = line_points[j]
            # Рисуем точку с заданной толщиной
            for dx in range(-width // 2, width // 2 + 1):
                for dy in range(-width // 2, width // 2 + 1):
                    if dx * dx + dy * dy <= (width / 2) ** 2:
                        draw.point((x + dx, y + dy), fill=color)


def draw_dashed_circle_bresenham(draw, x0, y0, radius, dash_count=6, color='purple', width=2):
    # Вычисляем углы для штрихов
    dash_angle = 30  # 30 градусов на штрих
    gap_angle = 30  # 30 градусов на пропуск

    # Рисуем каждый штрих
    for i in range(dash_count):
        start_angle = i * (dash_angle + gap_angle)
        end_angle = start_angle + dash_angle

        # Получаем точки для дуги
        arc_points = bresenham_arc(x0, y0, radius, start_angle, end_angle)

        # Рисуем точки дуги
        for x, y in arc_points:
            # Рисуем точку с заданной толщиной
            for dx in range(-width // 2, width // 2 + 1):
                for dy in range(-width // 2, width // 2 + 1):
                    if dx * dx + dy * dy <= (width / 2) ** 2:
                        draw.point((x + dx, y + dy), fill=color)


def draw_triangle_bresenham(draw, A, B, C, outline='black', fill_color=None, texture=None, width=2):
    # Рисуем контур треугольника
    draw_solid_line_bresenham(draw, A[0], A[1], B[0], B[1], color=outline, width=width)
    draw_solid_line_bresenham(draw, B[0], B[1], C[0], C[1], color=outline, width=width)
    draw_solid_line_bresenham(draw, C[0], C[1], A[0], A[1], color=outline, width=width)

    # Заливка треугольника
    if fill_color or texture:
        # Находим bounding box треугольника
        min_x = min(A[0], B[0], C[0])
        max_x = max(A[0], B[0], C[0])
        min_y = min(A[1], B[1], C[1])
        max_y = max(A[1], B[1], C[1])

        # Если есть текстура, загружаем и масштабируем ее
        if texture:
            try:
                # Загружаем текстуру
                texture_img = Image.open(texture)
                # Масштабируем текстуру под размер треугольника
                tri_width = max_x - min_x
                tri_height = max_y - min_y
                texture_resized = texture_img.resize((tri_width, tri_height))

                # Заливаем треугольник текстурой
                for x in range(min_x, max_x + 1):
                    for y in range(min_y, max_y + 1):
                        # Проверяем, находится ли точка внутри треугольника
                        if is_point_in_triangle(x, y, A, B, C):
                            # Вычисляем координаты в текстуре
                            tex_x = x - min_x
                            tex_y = y - min_y
                            # Получаем цвет из текстуры
                            if 0 <= tex_x < texture_resized.width and 0 <= tex_y < texture_resized.height:
                                color = texture_resized.getpixel((tex_x, tex_y))
                                draw.point((x, y), fill=color)
            except Exception as e:
                print(f"Ошибка загрузки текстуры: {e}")
                # Если не удалось загрузить текстуру, используем цветную заливку
                if fill_color:
                    for x in range(min_x, max_x + 1):
                        for y in range(min_y, max_y + 1):
                            if is_point_in_triangle(x, y, A, B, C):
                                draw.point((x, y), fill=fill_color)
        else:
            # Заливка цветом
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    if is_point_in_triangle(x, y, A, B, C):
                        draw.point((x, y), fill=fill_color)


def is_point_in_triangle(x, y, A, B, C):

    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    d1 = sign((x, y), A, B)
    d2 = sign((x, y), B, C)
    d3 = sign((x, y), C, A)

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not (has_neg and has_pos)


def draw_circle_bresenham(draw, x0, y0, radius, outline='green', fill='yellow', width=2):
    # Рисуем контур окружности
    circle_points = bresenham_circle_full(x0, y0, radius)
    for x, y in circle_points:
        # Рисуем точку с заданной толщиной
        for dx in range(-width // 2, width // 2 + 1):
            for dy in range(-width // 2, width // 2 + 1):
                if dx * dx + dy * dy <= (width / 2) ** 2:
                    draw.point((x + dx, y + dy), fill=outline)

    # Заливка окружности
    for x in range(x0 - radius, x0 + radius + 1):
        for y in range(y0 - radius, y0 + radius + 1):
            if (x - x0) ** 2 + (y - y0) ** 2 <= radius ** 2:
                draw.point((x, y), fill=fill)


def draw_scene_with_bresenham(texture_path=None):
    # Создаем изображение
    width, height = 400, 300
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # 1. Рисуем сплошную линию на заднем плане с помощью Брезенхема
    line_start = (0, 6.5)
    line_end = (200, 110)
    draw_solid_line_bresenham(draw, int(line_start[0]), int(line_start[1]),
                              int(line_end[0]), int(line_end[1]),
                              color='gray', width=1)

    # 2. Рисуем дугу с центром в (100,100), начинающуюся от (200,110)
    arc_center = (100, 100)
    start_point = (200, 110)

    # Вычисляем начальный угол от центра к начальной точке
    dx = start_point[0] - arc_center[0]
    dy = start_point[1] - arc_center[1]
    start_angle_rad = math.atan2(dy, dx)
    start_angle_deg = math.degrees(start_angle_rad)
    if start_angle_deg < 0:
        start_angle_deg += 360

    # Конечный угол - на 135 градусов по часовой стрелке
    end_angle_deg = start_angle_deg - 135
    if end_angle_deg < 0:
        end_angle_deg += 360

    # Радиус дуги - расстояние от центра до начальной точки
    arc_radius = math.sqrt(dx ** 2 + dy ** 2)

    # Рисуем дугу с помощью Брезенхема
    arc_points = bresenham_arc(arc_center[0], arc_center[1], int(arc_radius),
                               start_angle_deg, end_angle_deg)
    for x, y in arc_points:
        draw.point((x, y), fill='orange')

    # 3. Координаты основного треугольника
    A = (60, 130)
    B = (100, 50)
    C = (140, 130)

    # 4. Координаты штрихового треугольника (оконтовка)
    A_dash = (56, 133)
    B_dash = (100, 45)
    C_dash = (144, 133)

    # 5. Рисуем треугольник с помощью Брезенхема
    # Если указан путь к текстуре, используем ее для заливки
    if texture_path:
        draw_triangle_bresenham(draw, A, B, C, outline='black', texture=texture_path, width=2)
    else:
        draw_triangle_bresenham(draw, A, B, C, outline='black', fill_color='lightblue', width=2)

    # 6. Рисуем штриховую оконтовку треугольника с помощью Брезенхема
    draw_dashed_line_bresenham(draw, A_dash[0], A_dash[1], B_dash[0], B_dash[1],
                               dash_count=6, color='red', width=2)
    draw_dashed_line_bresenham(draw, B_dash[0], B_dash[1], C_dash[0], C_dash[1],
                               dash_count=6, color='red', width=2)
    draw_dashed_line_bresenham(draw, C_dash[0], C_dash[1], A_dash[0], A_dash[1],
                               dash_count=6, color='red', width=2)

    # 7. Параметры окружности
    circle_center = (100, 100)
    circle_radius = 20
    inner_dash_radius = 17

    # 8. Рисуем основную окружность с помощью Брезенхема
    draw_circle_bresenham(draw, circle_center[0], circle_center[1],
                          circle_radius, outline='green', fill='yellow', width=2)

    # 9. Рисуем внутреннюю штриховую оконтовку для окружности с помощью Брезенхема
    draw_dashed_circle_bresenham(draw, circle_center[0], circle_center[1],
                                 inner_dash_radius, dash_count=6, color='purple', width=2)


    return image

# Создаем изображение с текстурой для треугольника
try:
    img_texture = draw_scene_with_bresenham('task.png')
    img_texture.save('scene_with_bresenham_texture.png')
    print("Изображение с текстурой треугольника сохранено как 'scene_with_bresenham_texture.png'")
except Exception as e:
    print(f"Не удалось создать изображение с текстурой: {e}")

# Инструкция для пользователя
print("\n" + "=" * 50)
print("ИНСТРУКЦИЯ:")
print("1. Для использования текстуры передайте путь к файлу в функцию:")
print("   draw_scene_with_bresenham('path/to/your/texture.jpg')")
print("2. Форматы: JPEG, PNG, BMP и другие поддерживаемые Pillow")
print("3. Текстура будет автоматически масштабирована под размер треугольника")
print("=" * 50)