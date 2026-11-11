"""Exporta o desenho de montagem e o cobre reais. Requer KiCad, pdftoppm e Pillow."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

PROJECT = Path(__file__).resolve().parents[1] / "docs/hardware/kicad/rover_pcb_v2_chassi"
BOARD = PROJECT / "rover_pcb_v2_chassi.kicad_pcb"


def kicad_cli():
    candidate = shutil.which("kicad-cli")
    if candidate:
        return candidate
    installations = Path(os.environ.get("ProgramFiles", "")) / "KiCad"
    for executable in sorted(installations.glob("*/bin/kicad-cli.exe"), reverse=True):
        return str(executable)
    raise FileNotFoundError("Inclua kicad-cli no PATH.")


def render(directory, name, layers, options, ink):
    pdf = directory / f"{name}.pdf"
    subprocess.run([kicad_cli(), "pcb", "export", "pdf", "--mode-single", "--black-and-white",
                    "--layers", layers, *options, "-o", str(pdf), str(BOARD)], check=True)
    subprocess.run(["pdftoppm", "-singlefile", "-r", "320", "-png", str(pdf),
                    str(directory / name)], check=True)
    with Image.open(directory / f"{name}.png") as raster:
        gray = raster.convert("L")
    bounds = ImageChops.invert(gray).getbbox()
    if bounds is None:
        raise ValueError(f"Camadas vazias em {name}")
    gray = gray.crop(bounds)
    gray.thumbnail((780, 600), Image.Resampling.LANCZOS)
    return ImageOps.colorize(gray, ink, "white")


def font(size, bold=False):
    families = ("DejaVuSans-Bold.ttf", "arialbd.ttf") if bold else ("DejaVuSans.ttf", "arial.ttf")
    for family in families:
        try:
            return ImageFont.truetype(family, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def main():
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        front = render(directory, "montagem", "F.Fab,F.Silkscreen,Edge.Cuts",
                       ["--sketch-pads-on-fab-layers", "--exclude-value"], "#28484a")
        copper = render(directory, "cobre", "B.Cu,Edge.Cuts", ["--mirror"], "#94502c")
    canvas = Image.new("RGB", (1660, 770), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((32, 19), "Rover 4WD  /  Chassi V2", font=font(37, True), fill="#172e36")
    for x, title, view in ((32, "Montagem · vista superior", front),
                           (850, "Cobre inferior · visto pelo lado da solda", copper)):
        draw.text((x, 81), title, font=font(23, True), fill="#28444c")
        canvas.paste(view, (x, 129))
    output = PROJECT / "preview_pcb_top.png"
    canvas.save(output)
    print(output)


if __name__ == "__main__":
    main()

