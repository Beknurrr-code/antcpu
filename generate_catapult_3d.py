"""
Генератор 3D-модели катапульты «Резиновая» (масштаб 1:1, в миллиметрах)
для импорта в Tinkercad, Blender, SketchUp или 3D-печать (.STL и .OBJ)
и расчёта баллистических таблиц для отчёта STEM Олимпиады.
"""

import math
from pathlib import Path


def create_box_triangles(cx, cy, cz, dx, dy, dz, rot_z_deg=0.0, pivot=(0.0, 0.0)):
    """Создаёт 12 треугольников (6 граней) параллелепипеда с опциональным поворотом вокруг оси Z."""
    hx, hy, hz = dx / 2.0, dy / 2.0, dz / 2.0
    local_verts = [
        (cx - hx, cy - hy, cz - hz),
        (cx + hx, cy - hy, cz - hz),
        (cx + hx, cy + hy, cz - hz),
        (cx - hx, cy + hy, cz - hz),
        (cx - hx, cy - hy, cz + hz),
        (cx + hx, cy - hy, cz + hz),
        (cx + hx, cy + hy, cz + hz),
        (cx - hx, cy + hy, cz + hz),
    ]

    rad = math.radians(rot_z_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    px, py = pivot

    verts = []
    for vx, vy, vz in local_verts:
        if abs(rot_z_deg) > 1e-6:
            rx = px + (vx - px) * cos_a - (vy - py) * sin_a
            ry = py + (vx - px) * sin_a + (vy - py) * cos_a
            verts.append((rx, ry, vz))
        else:
            verts.append((vx, vy, vz))

    quads = [
        (0, 3, 2, 1),  # bottom (-Z)
        (4, 5, 6, 7),  # top (+Z)
        (0, 1, 5, 4),  # front (-Y)
        (2, 3, 7, 6),  # back (+Y)
        (1, 2, 6, 5),  # right (+X)
        (3, 0, 4, 7),  # left (-X)
    ]

    tris = []
    for a, b, c, d in quads:
        tris.append((verts[a], verts[b], verts[c]))
        tris.append((verts[a], verts[c], verts[d]))
    return tris


def build_catapult_mesh_mm():
    """
    Собирает 3D-модель катапульты «Резиновая» строго по ТЗ (Приложение №1):
    - Основание: рама в форме «Н» из брусков 15x15 мм (длина 360 мм, ширина 140 мм)
    - Опора: вертикальные стойки высотой 140 мм от основания до оси (норма 120-150 мм)
    - Ось: диаметр 5 мм (норма 4-6 мм), перпендикулярно плечу
    - Плечо (рычаг): длина 350 мм (норма 300-400 мм), сечение 15x15 мм, под углом 45°
    - Ограничитель: фиксирует угол вылета плеча на 45° к горизонтали
    - Корзина для груза и спусковой фиксатор
    В Tinkercad/Blender ось Z направлена вверх, поэтому:
      X — продольная ось (направление выстрела),
      Y — поперечная ось (ширина основания),
      Z — вертикальная ось (высота).
    """
    tris = []

    # 1. Основание («Н»-образная рама, сечение 15x15 мм)
    tris += create_box_triangles(0, -60, 7.5, 360, 15, 15)
    tris += create_box_triangles(0,  60, 7.5, 360, 15, 15)
    tris += create_box_triangles(-160, 0, 7.5, 20, 105, 15)
    tris += create_box_triangles(60,   0, 7.5, 25, 105, 15)
    tris += create_box_triangles(160,  0, 7.5, 20, 105, 15)

    # 2. Вертикальная опора (высота оси 140 мм от основания -> Z оси = 15 + 140 = 155 мм)
    pivot_x = 60.0
    pivot_z = 155.0
    tris += create_box_triangles(pivot_x, -45, 15 + 72.5, 18, 15, 145)
    tris += create_box_triangles(pivot_x,  45, 15 + 72.5, 18, 15, 145)

    # 3. Ограничитель угла 45° (стойки + верхняя перекладина)
    stopper_x = 5.0
    stopper_z = 192.0
    tris += create_box_triangles(stopper_x, -45, 15 + 90, 15, 15, 180)
    tris += create_box_triangles(stopper_x,  45, 15 + 90, 15, 15, 180)
    tris += create_box_triangles(stopper_x,   0, stopper_z, 18, 105, 15)

    # 4. Ось вращения (стержень 5x5 мм перпендикулярно плечу)
    tris += create_box_triangles(pivot_x, 0, pivot_z, 5, 120, 5)

    # 5. Спусковой фиксатор на задней перемычке основания
    tris += create_box_triangles(-160, 0, 22, 8, 25, 18)

    # 6. Плечо (рычаг длиной 350 мм, сечением 15x15 мм) и корзина под углом 45° в плоскости XZ
    def rotate_xz(parts, angle_deg, px, pz):
        rad = math.radians(angle_deg)
        ca, sa = math.cos(rad), math.sin(rad)
        out = []
        for t in parts:
            new_t = []
            for vx, vy, vz in t:
                rx = px + (vx - px) * ca - (vz - pz) * sa
                rz = pz + (vx - px) * sa + (vz - pz) * ca
                new_t.append((rx, vy, rz))
            out.append(tuple(new_t))
        return out

    arm_local = []
    # Плечо длиной 350 мм (рабочий конец 290 мм влево от оси, хвост 60 мм вправо)
    arm_local += create_box_triangles(pivot_x - 115, 0, pivot_z, 350, 15, 15)
    # Корзина (ложе) на рабочем конце плеча
    cup_x = pivot_x - 270
    arm_local += create_box_triangles(cup_x, 0, pivot_z + 10, 36, 36, 5)
    arm_local += create_box_triangles(cup_x - 16, 0, pivot_z + 17, 5, 36, 12)
    arm_local += create_box_triangles(cup_x + 16, 0, pivot_z + 17, 5, 36, 12)
    arm_local += create_box_triangles(cup_x, -16, pivot_z + 17, 32, 5, 12)
    arm_local += create_box_triangles(cup_x,  16, pivot_z + 17, 32, 5, 12)

    tris += rotate_xz(arm_local, -45.0, pivot_x, pivot_z)
    return tris


def export_ascii_stl(tris, filepath: Path):
    lines = ["solid catapult_rezinovaya"]
    for v1, v2, v3 in tris:
        ux, uy, uz = v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]
        vx, vy, vz = v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        length = math.hypot(nx, ny, nz) or 1.0
        nx, ny, nz = nx / length, ny / length, nz / length
        lines.append(f"  facet normal {nx:.4f} {ny:.4f} {nz:.4f}")
        lines.append("    outer loop")
        lines.append(f"      vertex {v1[0]:.3f} {v1[1]:.3f} {v1[2]:.3f}")
        lines.append(f"      vertex {v2[0]:.3f} {v2[1]:.3f} {v2[2]:.3f}")
        lines.append(f"      vertex {v3[0]:.3f} {v3[1]:.3f} {v3[2]:.3f}")
        lines.append("    endloop")
        lines.append("  endfacet")
    lines.append("endsolid catapult_rezinovaya")
    filepath.write_text("\n".join(lines), encoding="utf-8")


def export_obj(tris, filepath: Path):
    lines = ["# 3D Model: Catapult Rezinovaya (STEM Olympiad, units: mm)"]
    v_idx = 1
    for v1, v2, v3 in tris:
        for v in (v1, v2, v3):
            lines.append(f"v {v[0]:.3f} {v[1]:.3f} {v[2]:.3f}")
        lines.append(f"f {v_idx} {v_idx+1} {v_idx+2}")
        v_idx += 3
    filepath.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    out_dir = Path(__file__).parent
    mesh = build_catapult_mesh_mm()
    stl_path = out_dir / "catapult_rezinovaya.stl"
    obj_path = out_dir / "catapult_rezinovaya.obj"
    export_ascii_stl(mesh, stl_path)
    export_obj(mesh, obj_path)
    print(f"Generated {len(mesh)} triangles -> {stl_path.name}, {obj_path.name}")
