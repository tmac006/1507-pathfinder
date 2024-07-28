import cv2
import numpy as np
import math
import csv
import os

# 1 Pixel = 0.996 inches
P2I = lambda p: p * 0.996  # Convert Pixels to Inches
origin_set = False
origin = (0, 0)
pointList = []
relativeList = []
distances = []
angles = []
events = []

def CreateWindow():
    global img, original_img
    img_path = "2024Field.png"
    print(f"Trying to load image from {img_path}")
    if not os.path.exists(img_path):
        print(f"Error: The image file {img_path} does not exist.")
        return False
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error: The image file {img_path} could not be read.")
        return False
    print("Image loaded successfully")
    original_img = img.copy()
    img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    print("Image resized")
    cv2.namedWindow("1507 Pathfinding", cv2.WINDOW_NORMAL)
    cv2.imshow("1507 Pathfinding", img)
    cv2.setMouseCallback("1507 Pathfinding", CreatePath)
    print("Window created and mouse callback set")
    return True

def redraw_points():
    global img
    temp_img = img.copy()
    for point in relativeList:
        abs_point = (point[0] + origin[0], origin[1] - point[1])  # Convert relative to absolute
        cv2.circle(temp_img, abs_point, 3, (0, 225, 0), -1)
        cv2.putText(temp_img, f"({point[0]},{point[1]})", (abs_point[0] + 10, abs_point[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1, cv2.LINE_AA)
    for index, point in enumerate(relativeList):
        if index + 1 < len(relativeList):
            abs_point = (point[0] + origin[0], origin[1] - point[1])
            next_abs_point = (relativeList[index + 1][0] + origin[0], origin[1] - relativeList[index + 1][1])
            cv2.line(temp_img, abs_point, next_abs_point, (0, 225, 0), 2)
    for event in events:
        abs_event = (event[0] + origin[0], origin[1] - event[1])
        cv2.circle(temp_img, abs_event, 5, (0, 0, 255), -1)  # Draw event markers as larger red circles
        cv2.putText(temp_img, "Event", (abs_event[0] + 10, abs_event[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
    cv2.imshow("1507 Pathfinding", temp_img)
    print("Points and events redrawn")

def CreatePath(event, x, y, flags, params):
    global origin_set, origin, filename
    if event == cv2.EVENT_LBUTTONDOWN:
        if not origin_set:  # Sets the origin
            origin = (x, y)
            origin_set = True
            print(f"Origin set at {origin}")
        print(f"Point added at ({x}, {y})")
        relative_x = x - origin[0]
        relative_y = -(y - origin[1])  # Flip the y-coordinate
        pointList.append((x, y))
        relativeList.append((relative_x, relative_y))
        redraw_points()
    elif event == cv2.EVENT_RBUTTONDOWN:
        for point in relativeList:
            d = math.sqrt(point[0]**2 + point[1]**2)  # Distance from origin
            distances.append(round(P2I(d), 2))  # Distances in inches
            theta = math.degrees(math.atan2(point[1], point[0]))  # Angle from origin
            if theta < 0:  # Ensure angle is between 0 and 360
                theta += 360
            angles.append(round(theta, 2))

        redraw_points()

        print(f"Distances: {distances}")
        print(f"Angles: {angles}")  # Print for debug
        print(f"Relative points: {relativeList}")
        with open(filename + ".csv", 'w', newline='') as file:  # Write data to CSV
            writer = csv.writer(file)
            field = ["Distance (In)", "Direction (Deg)", "Points (x, y)", "Comments"]
            writer.writerow(field)
            for index, dist in enumerate(distances):
                writer.writerow([dist, angles[index], relativeList[index], ""])
            for event in events:
                writer.writerow(["", "", event, "Event"])
        print(f"Your values are now in {filename}.csv")

def ViewPath(file):
    if not CreateWindow():
        return
    readList = []
    with open(file + ".csv") as points:
        next(points)  # Skip the title row
        for row in points:
            if "Event" in row:
                continue
            x, y = map(int, row.split(",")[2].strip("() \n").split(","))
            readList.append((x, y))
    for index, point in enumerate(readList):
        print(f"Read point: {point}")
        pointList.append(point)
        relativeList.append((point[0], point[1]))
    redraw_points()

def main():
    global filename
    print("Pathfinding for 1507")
    choice = input("Would you like to place points or read from a CSV file? (P/R):")
    if choice.upper() == 'P':
        filename = input("Name the file you would like your numbers to go to: ")
        print("Left Click To Place Points, Right Click To Finish Placing Points")
        if CreateWindow():
            print("Entering main loop")
            while True:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):  # Press 'q' to exit
                    break
                elif key == ord('x'):  # Press 'x' to place an event marker
                    if origin_set:
                        event_x, event_y = relativeList[-1]  # Use the last placed point as the event marker
                        events.append((event_x, event_y))
                        print(f"Event marker placed at ({event_x}, {event_y})")
                        redraw_points()
            cv2.destroyAllWindows()
            print("Exiting main loop and closing windows")
    elif choice.upper() == 'R':
        file = input("What file would you like to view from? (do not add file extension): ")
        ViewPath(file)
        print("Entering main loop")
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # Press 'q' to exit
                break
        cv2.destroyAllWindows()
        print("Exiting main loop and closing windows")

if __name__ == "__main__":
    main()
