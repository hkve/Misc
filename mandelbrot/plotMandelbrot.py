import numpy as np
import matplotlib.pyplot as plt
import os
import argparse


def draw(image, extent, points):    
    fig, ax = plt.subplots()
    image = np.where(image < 5, 0, image-5)
    ax.imshow(image, extent=extent, cmap="RdGy", interpolation="nearest")
    ax.set(xlabel=r"$Re(z)$", ylabel=r"$Im(z)$", title="The Mandelbrot set")    
    plt.show()

def load_data(filename):
    data = np.loadtxt(filename, skiprows=1)
    with open(filename) as file:
        x0, x1, nx, y0, y1, ny = file.readline().split()
   
    nx, ny = int(nx), int(ny)
    extent = [float(x0), float(x1), float(y0), float(y1)]
    
    return data.reshape(ny,nx), extent, [nx, ny]

def main(run, x0, x1, y0, y1, nx, ny):
    filename = f"mandel_{x0}_{x1}_{y0}_{y1}_{nx}_{ny}.dat"
    
    
    if run:
        os.system(f"./mandelbrot.o {x0} {x1} {nx} {y0} {y1} {ny} {filename}")
    if not filename in os.listdir():
        print("missing datafile, set add flag -r (--run) to create datafile")
        exit()

    data, extent, points = load_data(filename)
    draw(data, extent, points)

if __name__ == "__main__":
    if not "mandelbrot.o" in os.listdir():
        os.system("gcc mandelbrot.c -o mandelbrot.o -lm")

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--run", action="store_true")
    parser.add_argument("-x0", default=-3, type=float)
    parser.add_argument("-x1", default=1.5, type=float)
    parser.add_argument("-y0", default=-1.5, type=float)
    parser.add_argument("-y1", default=1.5, type=float)
    parser.add_argument("-nx", default=1000, type=int)
    parser.add_argument("-ny", default=1000, type=int)

    args = vars(parser.parse_args())

    x0 = args["x0"]
    x1 = args["x1"]
    y0 = args["y0"]
    y1 = args["y1"]
    nx = args["nx"]
    ny = args["ny"]
    run = args["run"]

    main(run, x0, x1, y0, y1, nx, ny)
    