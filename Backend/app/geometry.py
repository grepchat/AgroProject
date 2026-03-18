from typing import Tuple


def pixels_to_greenhouse_coords(
    x_px: float,
    y_px: float,
    image_width: int,
    image_height: int,
) -> Tuple[float, float]:
    """
    Простейший пример: линейное преобразование в метры
    (нужно заменить на калиброванную модель/матрицу).
    """

    # Допустим, один кадр покрывает 2м по ширине и 1м по высоте
    greenhouse_width_m = 2.0
    greenhouse_height_m = 1.0

    x_m = x_px / image_width * greenhouse_width_m
    y_m = y_px / image_height * greenhouse_height_m

    return x_m, y_m
