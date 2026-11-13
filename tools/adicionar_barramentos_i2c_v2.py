"""Adiciona três saídas I2C à PCB V2 preservando uma única face de cobre."""

from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(x), mm(y))


def close_to(vector: pcbnew.VECTOR2I, x: float, y: float) -> bool:
    return abs(vector.x - mm(x)) <= 2 and abs(vector.y - mm(y)) <= 2


def add_route(
    board: pcbnew.BOARD,
    net_name: str,
    coordinates: list[tuple[float, float]],
    width: float,
) -> None:
    for start, end in zip(coordinates, coordinates[1:]):
        segment = pcbnew.PCB_TRACK(board)
        segment.SetLayer(pcbnew.B_Cu)
        segment.SetNet(board.FindNet(net_name))
        segment.SetWidth(mm(width))
        segment.SetStart(point(*start))
        segment.SetEnd(point(*end))
        board.Add(segment)


def find_segment(
    tracks: list[pcbnew.PCB_TRACK],
    net_name: str,
    start: tuple[float, float],
    end: tuple[float, float],
) -> pcbnew.PCB_TRACK:
    for track in tracks:
        if track.GetNetname() != net_name:
            continue
        direct = close_to(track.GetStart(), *start) and close_to(track.GetEnd(), *end)
        reverse = close_to(track.GetStart(), *end) and close_to(track.GetEnd(), *start)
        if direct or reverse:
            return track
    raise RuntimeError(f"Trecho não encontrado: {net_name} {start} -> {end}")


def add_wire_jumper(
    board: pcbnew.BOARD,
    footprint_dir: Path,
    reference: str,
    net_name: str,
    start: tuple[float, float],
    end: tuple[float, float],
    overlay_existing_holes: tuple[bool, bool] = (False, False),
) -> None:
    """Representa um fio isolado no lado dos componentes, sem cobre em F.Cu."""
    jumper = pcbnew.FootprintLoad(str(footprint_dir), "J3")
    if jumper is None:
        raise RuntimeError("Footprint Rover:J3 não encontrado")
    jumper.SetReference(reference)
    jumper.SetValue("FIO JUMPER ISOLADO")
    jumper.SetBoardOnly(True)
    jumper.SetPosition(point(0, 0))
    jumper.SetPath(pcbnew.KIID_PATH())
    jumper.SetDuplicatePadNumbersAreJumpers(True)
    for pad, position, overlay in zip(
        jumper.Pads(), (start, end), overlay_existing_holes, strict=True
    ):
        pad.SetPosition(point(*position))
        pad.SetNumber("1")
        pad.SetNet(board.FindNet(net_name))
        pad.SetPinFunction(net_name.removeprefix("/"))
        if overlay:
            # O furo físico já pertence ao conector original. Esta pequena
            # ilha SMD em B.Cu só informa ao KiCad que o fio usa aquele ponto.
            layers = pcbnew.LSET()
            layers.AddLayer(pcbnew.B_Cu)
            layers.AddLayer(pcbnew.B_Mask)
            pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            pad.SetDrillSize(point(0, 0))
            pad.SetLayerSet(layers)
            pad.SetSize(point(1.00, 1.00))
        else:
            pad.SetSize(point(1.50, 1.50))
            pad.SetDrillSize(point(0.80, 0.80))
    board.Add(jumper)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("entrada", type=Path)
    parser.add_argument("saida", type=Path)
    args = parser.parse_args()

    board = pcbnew.LoadBoard(str(args.entrada))
    footprint_dir = args.entrada.parent / "Rover.pretty"
    original_tracks = board.GetTracks()

    # Abre espaço para o bloco I2C. WS e BCLK são reroteados em B.Cu; DIN e
    # TEMP usam fios isolados no lado dos componentes como crossovers reais.
    removals = (
        ("/I2S-WS", (118.928, 77.432), (131.120, 89.624)),
        ("/I2S-WS", (131.120, 89.624), (136.200, 89.624)),
        ("/I2S-BCLK", (117.397487, 76.917487), (132.644, 92.164)),
        ("/I2S-BCLK", (132.644, 92.164), (136.200, 92.164)),
        ("/I2S-DIN", (122.738, 77.940), (122.738, 80.226)),
        ("/I2S-DIN", (122.738, 80.226), (130.866, 88.354)),
        ("/I2S-DIN", (130.866, 88.354), (136.708, 88.354)),
        ("/I2S-DIN", (136.708, 88.354), (137.470, 89.116)),
        ("/I2S-DIN", (137.470, 89.116), (137.470, 93.434)),
        ("/TEMP-DATA", (117.150, 84.290), (124.770, 91.910)),
        ("/TEMP-DATA", (124.770, 91.910), (124.770, 100.704)),
    )
    tracks_to_remove = [
        find_segment(original_tracks, net, start, end)
        for net, start, end in removals
    ]
    for track in tracks_to_remove:
        board.Remove(track)

    # Três fileiras de ilhas para fios, logo abaixo do conector OLED.
    net_names = ("/GND", "/+3V3", "/OLED-SCL", "/OLED-SDA")
    for index, y in enumerate((83.70, 86.90, 90.10), start=10):
        footprint = pcbnew.FootprintLoad(str(footprint_dir), "J9")
        if footprint is None:
            raise RuntimeError("Footprint Rover:J9 não encontrado")
        footprint.SetReference(f"J{index}")
        footprint.SetValue(f"I2C AUX {index - 9}")
        footprint.SetBoardOnly(True)
        footprint.SetPosition(point(123.00, y))
        footprint.SetPath(pcbnew.KIID_PATH())
        for pad, net_name in zip(footprint.Pads(), net_names, strict=True):
            pad.SetNet(board.FindNet(net_name))
        board.Add(footprint)

    # Os três novos barramentos e seus leques usam 1 mm.
    add_route(board, "/+3V3", [(125.54, 83.70), (125.54, 90.10)], 1.00)
    add_route(board, "/OLED-SCL", [(128.08, 83.70), (128.08, 90.10)], 1.00)
    add_route(board, "/OLED-SDA", [(130.62, 83.70), (130.62, 90.10)], 1.00)
    add_route(board, "/+3V3", [(125.54, 83.70), (127.564, 78.956)], 1.00)
    # SDA e SCL cruzam o pequeno degrau existente por fios superiores curtos.
    add_wire_jumper(
        board,
        footprint_dir,
        "JP3",
        "/OLED-SDA",
        (132.644, 78.956),
        (130.620, 83.700),
        (True, True),
    )
    add_wire_jumper(
        board,
        footprint_dir,
        "JP4",
        "/OLED-SCL",
        (130.104, 78.956),
        (128.080, 83.700),
        (True, True),
    )

    # WS/BCLK passam pelo corredor esquerdo e por baixo do novo bloco.
    add_route(
        board,
        "/I2S-WS",
        [
            (118.928, 77.432),
            (120.000, 78.504),
            (120.000, 92.000),
            (132.000, 92.000),
            (134.376, 89.624),
            (136.200, 89.624),
        ],
        0.32,
    )
    add_route(
        board,
        "/I2S-BCLK",
        [
            (117.397487, 76.917487),
            (119.300, 78.820),
            (119.300, 93.000),
            (134.500, 93.000),
            (135.336, 92.164),
            (136.200, 92.164),
        ],
        0.32,
    )

    # Crossovers longos: fios isolados soldados nas duas ilhas indicadas.
    add_wire_jumper(
        board,
        footprint_dir,
        "JP1",
        "/I2S-DIN",
        (122.738, 77.940),
        (137.470, 93.434),
    )
    add_wire_jumper(
        board,
        footprint_dir,
        "JP2",
        "/TEMP-DATA",
        (117.150, 84.290),
        (124.770, 96.000),
        (True, False),
    )
    add_route(board, "/TEMP-DATA", [(124.770, 96.000), (124.770, 100.704)], 0.32)

    board.BuildConnectivity()
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(args.saida), board)


if __name__ == "__main__":
    main()
