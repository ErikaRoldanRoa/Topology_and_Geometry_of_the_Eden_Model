import os
import numpy as np
from pathlib import Path
from datetime import datetime


def read_value(arr):
    while True:
        try:
            x = int(input())
            if x not in arr:
                raise ValueError
            break
        except ValueError:
            print("Oops!  That was no valid number.  Try again...")
    return x

print('Welcome to EDEN Model!')

print('Please, enter the desired dimension of your model (from 2 to 5): ')
dim = read_value([2, 3, 4, 5])

print('Do you have a file with a model? \n0 -- you want to generate a new model \n1 -- you have a file')
file = bool(read_value([0, 1]))

if dim <= 3:
    print('Do you want a picture of your model? (with a large model it can take time)  \n0 -- no \n1 -- yes')
    pic = bool(read_value([0, 1]))

"""NO FILE CASE"""
if not file:

    print('How many tiles would you like in your model?')
    while True:
        try:
            Time = int(input())
            break
        except ValueError:
            print("Oops!  That was no valid number.  Try again...")

    print('How many models would you like to build?')
    while True:
        try:
            num_models = int(input())
            break
        except ValueError:
            print("Oops!  That was no valid number.  Try again...")

    print('Do you want GUDHI barcode(s)? \n0 -- no \n1 -- yes')
    gudhi = bool(read_value([0, 1]))

    if gudhi:
        if dim == 2:
            print('What is the minimum length of the interval? Enter 1 number.')
        else:
            print('What is the minimum length of the interval? Enter '+str(dim-1)+' numbers one by one. ')
        length = []
        for i in range(dim-1):
            print("Minimal length for Betti_"+str(i+1)+':')
            while True:
                try:
                    x = int(input())
                    length.append(x)
                    break
                except ValueError:
                    print("Oops!  That was no valid number.  Try again...")

    for q in range(num_models):
        print("WORKING ON MODEL #"+str(q+1))
        now = datetime.now()
        dt_string = now.strftime("%d:%m:%Y_%H.%M.%S")
        if Time >= 1000:
            t = int(Time/1000)
            folder_name = str(dim)+'d/'+str(t)+'k_'+dt_string
        else:
            t = Time
            folder_name = str(dim)+'d/'+str(t)+'_'+dt_string
        os.makedirs(folder_name)

        if dim == 2:
            from e_2d import grow_eden, plot_b_per, draw_diagram_holes, num_holes, draw_tri_tetra, draw_barcode, \
                draw_polyomino, return_frequencies_1, draw_frequencies_1, convert_gudhi, gudhi_analysis
            print("Building a model...")
            Eden, Perimeter, Betti_1_total_vector, Betti_1_vector_changes, Barcode, Holes, Betti_1_total, \
                Created_holes, Process, Perimeter_len, Tags, Final_barcode = grow_eden(Time)

            print("\nCalculating frequencies of Betti_1...")
            freq, changes = return_frequencies_1(Betti_1_total_vector, Time)
            draw_frequencies_1(freq, changes, folder_name)
            print("Plotting the frequency of the volume of top dimensional \"holes\"...")
            draw_diagram_holes(Created_holes, Holes, folder_name)
            print("Plotting the growth rates of Betti numbers and the perimeter...")
            plot_b_per(Betti_1_total_vector, Perimeter_len, Time, folder_name)
            print("Plotting the frequency of the number of top dimensional holes for specific shapes with 3 and 4 cells...")
            Tromino, Tromino_f, Tetromino, Tetromino_f = num_holes(Created_holes, Holes)
            draw_tri_tetra(Tromino, Tromino_f, Tetromino, Tetromino_f, folder_name)

            # draw_barcode(Barcode, Time)
            if pic:
                print("\nDrawing the complex...")
                draw_polyomino(Eden, Time, folder_name)
            if gudhi:
                print("\nCreating Gudhi file...")
                Filename = convert_gudhi(Process, folder_name)
                print("Drawing Barcodes...")
                gudhi_analysis(Filename, Final_barcode, folder_name, length)
        elif dim == 3:
            from e_3d import grow_eden, return_frequencies_1, draw_frequencies_1, num_holes, draw_tri_tetra, plot_b_per,\
                return_frequencies_2, draw_frequencies_2, grow_eden_debugging, convert_gudhi, gudhi_analysis
            from e_2d import draw_diagram_holes
            print("\nBuilding a model...")
            Eden, Perimeter, Betti_2_total_vector, Betti_2_vector_changes, Barcode, Holes, Betti_1_total, \
                Betti_1_total_vector, Created_holes, Process, Perimeter_len, Skipped, I, Final_barcode = grow_eden(Time)

            print("\nCalculating frequencies of Betti_1...")
            freq, changes = return_frequencies_1(Betti_1_total_vector, Time)
            draw_frequencies_1(freq, changes, folder_name)
            print("\nCalculating frequencies of Betti_2...")
            freq, changes = return_frequencies_2(Betti_2_total_vector, Time)
            draw_frequencies_2(freq, changes, folder_name)

            print("Plotting the frequency of the volume of top dimensional \"holes\"...")
            draw_diagram_holes(Created_holes, Holes, folder_name)
            print("Plotting the growth rates of Betti numbers and the perimeter...")
            plot_b_per(Betti_1_total_vector, Betti_2_total_vector, Perimeter_len, Time, 0, folder_name)
            print("Plotting the frequency of the number of top dimensional holes for specific shapes with 3 and 4 cells...")
            Tricube, Tricube_f, Tetracube, Tetracube_f = num_holes(Created_holes, Holes)
            draw_tri_tetra(Tricube, Tricube_f, Tetracube, Tetracube_f, folder_name)

            if gudhi:
                print("\nCreating Gudhi file...")
                Filename = convert_gudhi(Process, folder_name)
                print("\nDrawing Barcodes...")
                gudhi_analysis(Filename, Final_barcode, folder_name, length)

            if pic:
                a = 1
                f = open(folder_name+"/MAYA.txt", "w+")
                f.write("import maya.cmds as cmds \nimport math as m \n"
                        "import os,sys \nEden = " + str(Process)+"\nt = len(Eden)"
                        "\nfor i in range(0,t):\n\taux = cmds.polyCube()"
                        "\n\tcmds.move(Eden[i][0],Eden[i][1],Eden[i][2],aux)")
                f.close()
                print("We created txt file \"MAYA\" for you. Just copy paste its content to MAYA!")
        elif dim == 4:
            from e_4d import grow_eden, draw_frequencies_3, return_frequencies_3, plot_b_per,\
                convert_gudhi, gudhi_analysis
            from e_2d import draw_diagram_holes
            Eden, Perimeter, betti_3_vector, barcode, Holes, betti_3_total, Created_holes, Process, Perimeter_len,\
                Betti_3_total_vector, Final_barcode = grow_eden(Time)

            print("\nCalculating frequencies of Betti_3...")
            freq, changes = return_frequencies_3(Betti_3_total_vector, Time)
            draw_frequencies_3(freq, changes, folder_name)
            try:
                print("Plotting the frequency of the volume of top dimensional \"holes\"...")
                draw_diagram_holes(Created_holes, Holes, folder_name)
            except IndexError:
                print("Unable to draw \"Diagram of Holes\". The Complex is too small.")
            try:
                print("Plotting the growth rates of Betti number and the perimeter...")
                plot_b_per(Betti_3_total_vector, Perimeter_len, Time, 0, folder_name)
            except RuntimeError:
                print("Unable to draw \"Betti vs Perimeter\". The Complex is too small.")

            if gudhi:
                print("\nCreating Gudhi file...")
                Filename = convert_gudhi(Process, folder_name)
                print("\nDrawing Barcodes...")
                gudhi_analysis(Filename, Final_barcode, folder_name, length)
        elif dim == 5:
            from e_5d import grow_eden, draw_frequencies_4, return_frequencies_4, plot_b_per,\
                convert_gudhi, gudhi_analysis
            from e_2d import draw_diagram_holes
            Eden, Perimeter, Betti_4_total_vector, Barcode, Holes, Created_holes, Process, Perimeter_len, \
                Final_barcode = grow_eden(Time)

            print("\nCalculating frequencies of Betti_4...")
            freq, changes = return_frequencies_4(Betti_4_total_vector, Time)
            changes = np.array(changes)
            if np.all((changes == 0)):
                print("Betti_4 is always 0. Plot can't be generated")
            else:
                draw_frequencies_4(freq, changes, folder_name)
            try:
                print("Plotting the frequency of the volume of top dimensional \"holes\"...")
                draw_diagram_holes(Created_holes, Holes, folder_name)
            except IndexError:
                print("Unable to draw \"Diagram of Holes\". The Complex is too small.")
            print("Plotting the growth rates of Betti numbers and the perimeter...")
            plot_b_per(Betti_4_total_vector, Perimeter_len, Time, 0, folder_name)

            if gudhi:
                print("\nCreating Gudhi file...")
                Filename = convert_gudhi(Process, folder_name)
                print("\nComputing Persistence Homology with GUDHI...")
                gudhi_analysis(Filename, Final_barcode, folder_name, length)

"""FILE CASE"""
if file:
    print('What is the format of the file? \n0 -- list of tuples \n1 -- Perseus')
    file_format = read_value([0, 1])
    print('Name of the file (for example, filename.txt):')
    filename = str(input())
    while not Path(str(dim)+"d/files/"+filename).exists():
        print("Oops!  That was no valid name.  Try again...")
        filename = str(input())
    from e_2d import read_eden_perseus, read_eden_txt
    if file_format == 1:
        Eden_f = read_eden_perseus(str(dim)+"d/files/"+filename)
    else:
        Eden_f = read_eden_txt(str(dim)+"d/files/"+filename)
    Eden = [x[0] for x in Eden_f]
    Process = Eden.copy()
    Times = [x[1] for x in Eden_f]
    Time = len(Eden)
    now = datetime.now()
    dt_string = now.strftime("%d:%m:%Y_%H.%M.%S")
    folder_name = str(dim)+'d/'+filename
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    print('Do you want GUDHI barcode(s)? \n0 -- no \n1 -- yes')
    gudhi = bool(read_value([0, 1]))

    if gudhi:
        if dim == 2:
            print('What is the minimum length of the interval? Enter 1 number.')
        else:
            print('What is the minimum length of the interval? Enter '+str(dim-1)+' numbers one by one. ')
        length = []
        for i in range(dim-1):
            print("Minimal length for Betti_"+str(i+1)+':')
            while True:
                try:
                    x = int(input())
                    length.append(x)
                    break
                except ValueError:
                    print("Oops!  That was no valid number.  Try again...")

    if dim == 2:
        from e_2d import grow_eden_debugging, plot_b_per, draw_diagram_holes, num_holes, draw_tri_tetra, draw_barcode, draw_polyomino,\
            return_frequencies_1, draw_frequencies_1, convert_gudhi, gudhi_analysis

        print("\nComputing persistent homology...")
        Eden, Perimeter, Betti_1_vector, Betti_1_total_vector, Barcode, Holes, Betti_1_total, Betti_1_euler_total, \
            Created_holes, Tags, Final_barcode, Perimeter_len = grow_eden_debugging(len(Eden), Eden)

        print("\nCalculating frequencies of Betti_1...")
        freq, changes = return_frequencies_1(Betti_1_total_vector, Time)
        draw_frequencies_1(freq, changes, folder_name)
        print("Plotting the frequency of the volume of top dimensional \"holes\"...")
        draw_diagram_holes(Created_holes, Holes, folder_name)
        print("Plotting the growth rates of Betti numbers and the perimeter...")
        plot_b_per(Betti_1_total_vector, Perimeter_len, Time, folder_name)
        print("Plotting the frequency of the number of top dimensional holes for specific shapes with 3 and 4 cells...")
        Tromino, Tromino_f, Tetromino, Tetromino_f = num_holes(Created_holes, Holes)
        draw_tri_tetra(Tromino, Tromino_f, Tetromino, Tetromino_f, folder_name)

        # draw_barcode(Barcode, Time)
        if pic:
            print("Drawing the complex...")
            draw_polyomino(Eden, Time)
        if gudhi:
            if not os.path.exists(folder_name+'/gudhi.txt'):
                print("\nCreating Gudhi file...")
                Filename = convert_gudhi(Process, folder_name)
            print("\nDrawing Barcodes...")
            gudhi_analysis(Filename, Final_barcode, folder_name, length)

    elif dim == 3:
        from e_3d import return_frequencies_1, draw_frequencies_1, num_holes, draw_tri_tetra, plot_b_per,\
            return_frequencies_2, draw_frequencies_2, grow_eden_debugging, convert_gudhi, gudhi_analysis
        from e_2d import draw_diagram_holes

        print("\nComputing persistent homology...")
        Eden, Perimeter, Betti_2_total_vector, Betti_1_total_vector, Barcode, Holes, \
            Betti_2_total, Betti_1_total, Created_holes, Perimeter_len, \
            Final_barcode = grow_eden_debugging(len(Eden), Eden)

        print("\nCalculating frequencies of Betti_1...")
        freq, changes = return_frequencies_1(Betti_1_total_vector, Time)
        draw_frequencies_1(freq, changes, folder_name)
        print("\nCalculating frequencies of Betti_2...")
        freq, changes = return_frequencies_2(Betti_2_total_vector, Time)
        draw_frequencies_2(freq, changes, folder_name)

        print("Plotting the frequency of the volume of top dimensional \"holes\"...")
        draw_diagram_holes(Created_holes, Holes, folder_name)
        print("Plotting the growth rates of Betti numbers and the perimeter...")
        plot_b_per(Betti_1_total_vector, Betti_2_total_vector, Perimeter_len, Time, 0, folder_name)
        print("Plotting the frequency of the number of top dimensional holes for specific shapes with 3 and 4 cells...")
        Tricube, Tricube_f, Tetracube, Tetracube_f = num_holes(Created_holes, Holes)
        draw_tri_tetra(Tricube, Tricube_f, Tetracube, Tetracube_f, folder_name)

        if gudhi:
            if not os.path.exists(folder_name+'/gudhi.txt'):
                print("\nCreating Gudhi file...")
                Filename = convert_gudhi(Process, folder_name)
            print("\nDrawing Barcodes...")
            gudhi_analysis(Filename, Final_barcode, folder_name, length)

        if pic:
            a = 1
            f = open("3d/"+str(int(Time/1000))+"k/MAYA.txt", "w+")
            f.write("import maya.cmds as cmds \nimport math as m \n"
                    "import os,sys \nEden = " + str(Process)+"\nt = len(Eden)"
                    "\nfor i in range(0,t):\n\taux = cmds.polyCube()"
                    "\n\tcmds.move(Eden[i][0],Eden[i][1],Eden[i][2],aux)")
            f.close()
            print("We created txt file \"MAYA\" for you. Just copy paste its content to MAYA!")
    elif dim == 4:
        from e_4d import grow_eden_debugging, draw_frequencies_3, return_frequencies_3, plot_b_per,\
            convert_gudhi, gudhi_analysis
        from e_2d import draw_diagram_holes

        print("\nComputing persistent homology...")
        Eden, Perimeter, betti_3_vector, barcode, Holes, betti_3_total, Created_holes, Perimeter_len,\
            Betti_3_total_vector, Final_barcode = grow_eden_debugging(len(Eden), Eden)

        print("\nCalculating frequencies of Betti_3...")
        freq, changes = return_frequencies_3(Betti_3_total_vector, Time)
        draw_frequencies_3(freq, changes, folder_name)
        try:
            print("Plotting the frequency of the volume of top dimensional \"holes\"...")
            draw_diagram_holes(Created_holes, Holes, folder_name)
        except IndexError:
            print("Unable to draw \"Diagram of Holes\". The Complex is too small.")
        try:
            print("Plotting the growth rates of Betti number and the perimeter...")
            plot_b_per(Betti_3_total_vector, Perimeter_len, Time, 0, folder_name)
        except RuntimeError:
            print("Unable to draw \"Betti vs Perimeter\". The Complex is too small.")

        if gudhi:
            if not os.path.exists(folder_name+'/gudhi.txt'):
                print("\nCreating Gudhi file...")
                Filename = convert_gudhi(Process, folder_name)
            print("\nDrawing Barcodes...")
            gudhi_analysis(Filename, Final_barcode, folder_name, length)


print("WE ARE DONE! CHECK THE FOLDER!")
