import math
import random
import cvzone
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import cv2

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8, maxHands=1)


class SnackGameClass:

    def __init__(self, path_food):
        self.points = []  # all points of the snake
        self.lengths = []  # distance between each point
        self.currentLength = 0  # total length of the snake
        self.allowedLength = 150  # total allowed Length
        self.previousHead = 0, 0  # previous head point
        self.imgFood = cv2.imread(path_food, cv2.IMREAD_UNCHANGED)
        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = 0, 0
        self.random_food_location()

        self.score = 0
        self.game_over = False

    def random_food_location(self):
        self.foodPoint = random.randint(100, 1000), random.randint(100, 600)

    def update(self, img_main, current_head):
        if self.game_over:
            cvzone.putTextRect(img_main, "Game Over", [300, 400], scale=7, thickness=5, offset=20)
            cvzone.putTextRect(img_main, f"score{self.score}", [300, 50], scale=3, thickness=3, offset=10)

        else:
            px, py = self.previousHead
            cx, cy = current_head

            self.points.append([cx, cy])
            distance = math.hypot(cx - px, cy - py)
            self.lengths.append(distance)
            self.currentLength += distance
            self.previousHead = cx, cy

            # Length reduction

            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break

            # Check if snake ate the Food
            rx, ry = self.foodPoint
            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and ry - self.hFood // 2 < cy < ry + self.hFood // 2:
                self.random_food_location()
                self.allowedLength += 50
                self.score += 1
                print(self.score)

            # Draw Snake
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:
                        cv2.line(img_main, self.points[i - 1], self.points[i], (0, 0, 255), 20)
                cv2.circle(img, self.points[-1], 20, (120, 120, 200), cv2.FILLED)

            # Draw food
            rx, ry = self.foodPoint
            img_main = cvzone.overlayPNG(img_main, self.imgFood, (rx - self.wFood // 2, ry - self.hFood // 2))

            # Check for Collision

            pts = np.array(self.points[:-2], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(img_main, [pts], False, (0, 200, 0), 3)
            min_distance = cv2.pointPolygonTest(pts, (cx, cy), True)

            if -1 <= min_distance <= 1:
                print(min_distance)
                self.game_over = True
                self.points = []  # all points of the snake
                self.lengths = []  # distance between each point
                self.currentLength = 0  # total length of the snake
                self.allowedLength = 150  # total allowed Length
                self.previousHead = 0, 0  # previous head point
                self.random_food_location()

        return img_main


# create object

game = SnackGameClass("Donut.png")

while True:
    try:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)
        if hands:
            lmList = hands[0]['lmList']
            pointIndex = lmList[8][0:2]
            img = game.update(img, pointIndex)
        cv2.imshow('Image', img)
        key = cv2.waitKey(1)
        if key == ord('r'):
            game.game_over = False
    except Exception as e:
        print("Exception happened: {}".format(e))
        continue
