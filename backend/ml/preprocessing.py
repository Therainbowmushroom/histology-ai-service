import os
import uuid
import openslide

from PIL import Image


def preprocess_slide(
    slide_path: str,
    output_dir: str,
    tile_size: int = 512,
    max_tiles: int = 100
):

    print("OPENING SLIDE", flush=True)

    slide = openslide.OpenSlide(slide_path)

    print("SLIDE OPENED", flush=True)
    print(f"DIMENSIONS: {slide.dimensions}", flush=True)

    print("LEVEL COUNT:", slide.level_count, flush=True)
    print("LEVEL DIMENSIONS:", slide.level_dimensions, flush=True)

    # Берём НЕ максимальный resolution
    level = min(2, slide.level_count - 1)

    level_width, level_height = slide.level_dimensions[level]

    print(f"USING LEVEL: {level}", flush=True)
    print(f"LEVEL SIZE: {level_width}x{level_height}", flush=True)

    tile_folder = os.path.join(
        output_dir,
        str(uuid.uuid4())
    )

    os.makedirs(tile_folder, exist_ok=True)

    tile_count = 0

    print("GENERATING TILES", flush=True)

    for x in range(0, level_width, tile_size):

        for y in range(0, level_height, tile_size):

            if tile_count >= max_tiles:

                print("MAX TILES REACHED", flush=True)

                return tile_folder

            print(f"READ TILE {tile_count}", flush=True)

            print(f"x={x}, y={y}, level={level}, tile_size={tile_size}")
            print(f"level_downsamples[{level}] = {slide.level_downsamples[level]}")
            print(f"location = ({x * slide.level_downsamples[level]}, {y * slide.level_downsamples[level]})")
            # Отладка перед read_region
            print(f"x={x}, y={y}, level={level}, tile_size={tile_size}")
            print(f"level_downsamples[{level}] = {slide.level_downsamples[level]}")
            loc_x = x * slide.level_downsamples[level]
            loc_y = y * slide.level_downsamples[level]
            print(f"loc_x={loc_x} (type {type(loc_x)}), loc_y={loc_y} (type {type(loc_y)})")
            print(f"level type: {type(level)}")
            print(f"tile_size type: {type(tile_size)}")
            tile = slide.read_region(
                (int(loc_x), int(loc_y)),
                int(level),
                (int(tile_size), int(tile_size))
            )

            tile = tile.convert("RGB")

            tile_path = os.path.join(
                tile_folder,
                f"tile_{tile_count}.jpg"
            )

            tile.save(tile_path, quality=90)

            print(f"SAVED TILE {tile_count}", flush=True)

            tile_count += 1

    print(f"TOTAL TILES: {tile_count}", flush=True)

    return tile_folder