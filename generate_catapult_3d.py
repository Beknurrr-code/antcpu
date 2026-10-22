"""
Генератор точной 3D-модели катапульты «Резиновая» по реальным замерам и фото команды
(масштаб 1:1, единицы измерения: миллиметры, для Tinkercad / Blender / SketchUp):
- Основание: длина 180 мм, ширина 140 мм, сечение бруса 18x18 мм
- Опора: две вертикальные стойки высотой 160 мм, сечением 18x18 мм
- Плечо (рычаг): длина 300 мм, сечение 15x15 мм (под углом 45°)
- Ось вращения: диаметр 6 мм (болт М6 на высоте 142 мм от основания)
- Ограничитель: столбик 18x18 мм со скосом 69 мм / 59 мм под углом 45°
- Корзина: круглая чаша с внутренним диаметром 55 мм и высотой 11 мм
- Спусковой фиксатор: двойное ушко 16x16 мм и стальная чека длиной 144 мм
"""

import math
from pathlib import Path


def create_box_triangles(cx, cy, cz, dx, dy, dz):
    hx, hy, hz = dx / 2.0, dy / 2.0, dz / 2.0
    verts = [
        (cx - hx, cy - hy, cz - hz),
        (cx + hx, cy - hy, cz - hz),
        (cx + hx, cy + hy, cz - hz),
        (cx - hx, cy + hy, cz - hz),
        (cx - hx, cy - hy, cz + hz),
        (cx + hx, cy - hy, cz + hz),
        (cx + hx, cy + hy, cz + hz),
        (cx - hx, cy + hy, cz + hz),
    ]
    quads = [
        (0, 3, 2, 1),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (2, 3, 7, 6),
        (1, 2, 6, 5),
        (3, 0, 4, 7),
    ]
    tris = []
    for a, b, c, d in quads:
        tris.append((verts[a], verts[b], verts[c]))
        tris.append((verts[a], verts[c], verts[d]))
    return tris


def create_cylinder_cup_triangles(cx, cy, cz_bottom, inner_d, outer_d, height, segs=24):
    """Создаёт круглую чашу (корзину Ø55 мм, высота 11 мм)."""
    tris = []
    r_in = inner_d / 2.0
    r_out = outer_d / 2.0
    for i in range(segs):
        a0 = (i / segs) * math.pi * 2.0
        a1 = ((i + 1) / segs) * math.pi * 2.0
        c0, s0 = math.cos(a0), math.sin(a0)
        c1, s1 = math.cos(a1), math.sin(a1)

        # Дно чаши (толщина 2 мм)
        p_center = (cx, cy, cz_bottom + 2.0)
        p0 = (cx + c0 * r_in, cy + s0 * r_in, cz_bottom + 2.0)
        p1 = (cx + c1 * r_in, cy + s1 * r_in, cz_bottom + 2.0)
        tris.append((p_center, p0, p1))

        # Наружная стенка
        b0 = (cx + c0 * r_out, cy + s0 * r_out, cz_bottom)
        b1 = (cx + c1 * r_out, cy + s1 * r_out, cz_bottom)
        t0 = (cx + c0 * r_out, cy + s0 * r_out, cz_bottom + height)
        t1 = (cx + c1 * r_out, cy + s1 * r_out, cz_bottom + height)
        tris.append((b0, b1, t1))
        tris.append((b0, t1, t0))
    return tris


def rotate_xz(tris, angle_deg, px, pz):
    rad = math.radians(angle_deg)
    ca, sa = math.cos(rad), math.sin(rad)
    out = []
    for t in tris:
        new_t = []
        for vx, vy, vz in t:
            rx = px + (vx - px) * ca - (vz - pz) * sa
            rz = pz + (vx - px) * sa + (vz - pz) * ca
            new_t.append((rx, vy, rz))
        out.append(tuple(new_t))
    return out


def build_catapult_mesh_mm():
    tris = []
    # 1. Основание: длина 180 мм, ширина 140 мм, сечение 18x18 мм
    # Две продольные боковины по 180 мм (Y = -61 и Y = +61)
    tris += create_box_triangles(0, -61, 9, 180, 18, 18)
    tris += create_box_triangles(0,  61, 9, 180, 18, 18)

    # Три поперечины (задняя под фиксатор, средняя под опору, передняя под ограничитель)
    tris += create_box_triangles(-81, 0, 9, 18, 104, 18)
    tris += create_box_triangles(-5,  0, 9, 18, 104, 18)
    tris += create_box_triangles(43,  0, 9, 18, 104, 18)

    # 2. Двойная вертикальная опора: высота 160 мм, сечение 18x18 мм, зазор 19 мм под рычаг 15 мм
    pivot_x = -5.0
    pivot_z = 18.0 + 142.0  # ось на высоте 142 мм от основания (160 мм полная высота стойки)
    tris += create_box_triangles(pivot_x, -18.5, 18 + 80, 18, 18, 160)
    tris += create_box_triangles(pivot_x,  18.5, 18 + 80, 18, 18, 160)

    # 3. Ось вращения Ø 6 мм с гайками
    tris += create_box_triangles(pivot_x, 0, pivot_z, 6, 75, 6)

    # 4. Ограничитель на передней поперечине (высоты 69 мм и 59 мм, средняя 64 мм)
    stopper_x = 43.0
    tris += create_box_triangles(stopper_x, 0, 18 + 32, 18, 18, 64)

    # 5. Спусковой фиксатор на задней поперечине: двойное ушко 16x16 мм + чека 144 мм
    tris += create_box_triangles(-81, -5.5, 18 + 8, 16, 4.5, 16)
    tris += create_box_triangles(-81,  5.5, 18 + 8, 16, 4.5, 16)
    tris += create_box_triangles(-81,  0.0, 18 + 10, 3.5, 144, 3.5)

    # 6. Плечо (рычаг 300 мм, сечение 15x15 мм) + круглая корзина (внутр. Ø 55 мм, высота 11 мм)
    arm_local = []
    # Рычаг: нижнее плечо +110 мм, верхнее рабочее плечо -190 мм (итого 300 мм)
    arm_local += create_box_triangles(pivot_x - 40, 0, pivot_z, 300, 15, 15)
    # Болт крепления жгутов на нижнем конце рычага
    arm_local += create_box_triangles(pivot_x + 68, 0, pivot_z, 4.5, 38, 4.5)
    # Круглая корзина Ø 55 мм (наружный Ø 61 мм, высота 11 мм) на рабочем конце
    arm_local += create_cylinder_cup_triangles(pivot_x - 162, 0, pivot_z + 7.5, 55.0, 61.0, 11.0)

    tris += rotate_xz(arm_local, -45.0, pivot_x, pivot_z)
    return tris


def export_ascii_stl(tris, filepath: Path):
    lines = ["solid catapult_rezinovaya_photo_exact"]
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
    lines.append("endsolid catapult_rezinovaya_photo_exact")
    filepath.write_text("\n".join(lines), encoding="utf-8")


def export_obj(tris, filepath: Path):
    lines = ["# 3D Model: Catapult Rezinovaya (Exact Photo Replica, units: mm)"]
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
