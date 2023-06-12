import launchpad_py as launchpad
import random
import time


def clear_screen():
    print("Clearing")
    for y in range(9):
        for x in range(9):
            lp.LedCtrlXYByCode(x, y, 0)
            time.sleep(0.01)

def is_list_close(input_list, max_difference=1):
    big_num = input_list[0]
    small_num = input_list[0]
    for item in input_list:
        if item > big_num:
            big_num = item
        elif item < small_num:
            small_num = item
        if big_num - small_num > max_difference:
            return False
    if big_num - small_num <= max_difference:
        return True

def get_direction(input_list): # Input should be in the format [[x, y], [x, y], [x, y]]
    max_x = input_list[0][0]
    min_x = input_list[0][0]
    max_y = input_list[0][1]
    min_y = input_list[0][1]

    for item in input_list:
        if item[0] > max_x:
            max_x = item[0]
        elif item[0] < min_x:
            min_x = item[0]

        if item[1] > max_y:
            max_y = item[1]
        elif item[1] < min_y:
            min_y = item[1]

    range_x = max_x - min_x
    range_y = max_y - min_y
    try:
        if range_y / range_x < 0.4: # Motion is on the x-axis
            if input_list[0][0] < (min_x + range_x/2) < input_list[-1][0]:
                return "right"
            elif input_list[0][0] > (min_x + range_x/2) > input_list[-1][0]:
                return "left"
            else:
                print("uh oh")
                return
    except ZeroDivisionError:
        pass
    try:
        if range_x / range_y < 0.34:
            if input_list[0][1] < (min_y + range_y/2) < input_list[-1][1]:
                return "down"
            elif input_list[0][1] > (min_y + range_y/2) > input_list[-1][1]:
                return "up"
            else:
                print("uh oh")
                return
    except ZeroDivisionError:
        print("no")
        return

def wait_for_gesture(timeout = 0, extra_interactions = []):
    """
    lp.ButtonFlush() should generally be called before running this function
    :param timeout: A maximum time in milliseconds to wait for a gesture. Default is 0, 0 is no timeout. A custom timeout is recommended, to prevent registering multiple touches as a gesture
    :return: If the command times out, an empty array is returned. Otherwise ["gesture direction", startx, starty, endx, endy] is returned
    """
    interactions = extra_interactions # [[x, y, ms_time], [x, y, ms_time]]
    #lp.ButtonFlush()
    start_time = round(time.monotonic() * 1000)
    if timeout == 0:
        end_time = ((time.monotonic() + 1000000000000) * 1000)
    else:
        end_time = round(start_time + timeout)
    now_time = round(time.monotonic() * 1000)

    while time.monotonic() * 1000 < end_time:
        btn_events = lp.ButtonStateXY()
        if btn_events != []: # Check if something actually happened
            if btn_events[2] > 0: # We only want to know if a button is pressed, not if it is released
                interactions.append([btn_events[0], btn_events[1], round(time.monotonic() * 1000)])
                print(interactions)
        if interactions != []: # This prevents an error due to accessing a non-existent index if the list is empty
            now_time = round(time.monotonic() * 1000)
            if len(interactions) >= 2 and now_time > interactions[-1][2] + 120:
                try_detect_gesture = True
                break # Go to after the while loop, where gesture is detected
            elif now_time > interactions[-1][2] + 120: # Clear the list of interactions if it has been too long since the last button, to prevent detecting multiple button presses
                interactions = []
                print("Cleared")

    if len(interactions) >= 2 and now_time > interactions[-1][2] + 120:
        if get_direction(interactions) == "right":  # Swipe to the right
            print("right")
            return True, ["right", interactions[0][0], interactions[0][1], interactions[-1][0], interactions[-1][1]]  # ["gesture direction", startx, starty, endx, endy]
        elif get_direction(interactions) == "left":  # Swipe to the left
            print("left")
            return True, ["left", interactions[0][0], interactions[0][1], interactions[-1][0], interactions[-1][1]]  # ["gesture direction", startx, starty, endx, endy]
        elif get_direction(interactions) == "down":  # Swipe down
            print("down")
            return True, ["down", interactions[0][0], interactions[0][1], interactions[-1][0], interactions[-1][1]]  # ["gesture direction", startx, starty, endx, endy]
        elif get_direction(interactions) == "up":  # Swipe up
            print("up")
            return True, ["up", interactions[0][0], interactions[0][1], interactions[-1][0], interactions[-1][1]]  # ["gesture direction", startx, starty, endx, endy]
        else:
            print("no gesture")
            return False, []
    else:
        print("no gesture yet")
        return False, interactions


lp = launchpad.LaunchpadLPX()
# Add an extra thing here if you want to use a different launchpad
if lp.Open(1, "launchpad x") or lp.Open(1, "lpx"):
    print("Launchpad X found")
else:
    print("Uh oh no can do - Is launchpad x connected?")
    time.sleep(7)

if lp.Open(1, "launchpad x") or lp.Open(1, "lpx"):
    print("Launchpad X found")
else:
    print("Big uh oh")
    exit()
clear_screen()


red = 5
green = 21
blue_food = 78
blue_snake = 29
game = True

while game:
    snake_coords = [[0, 1], [1, 1], [2, 1]]
    max_score = len(snake_coords)
    eaten = False
    sad_red_snake = False
    food_coord = [6, 4]
    direction = "x+"
    extra_interactions = []
    game_running = True

    lp.ButtonFlush()
    while game_running:
        #lp.LedAllOn(0)  # Turn off all the LEDs briefly
        print(snake_coords)
        if len(snake_coords) > max_score:
            max_score = len(snake_coords)
        if len(snake_coords) < 1:
            print("Game Over! Score is " + str(max_score))
            game_running = False
            break
        lp.LedCtrlXYByCode(food_coord[0], food_coord[1], blue_food)
        lp.LedCtrlXYByCode(snake_coords[-1][0], snake_coords[-1][1], red)
        for coord in snake_coords[:-1]:
            #if coord != snake_coords[-1]: # Body of the snake, head has already been set
            if sad_red_snake:
                lp.LedCtrlXYByCode(coord[0], coord[1], red)
            elif not eaten:
                lp.LedCtrlXYByCode(coord[0], coord[1], green)
            elif eaten:
                lp.LedCtrlXYByCode(coord[0], coord[1], blue_snake)
        eaten = False
        sad_red_snake = False
        did_change_pos = False
        end_time = round(time.monotonic() * 1000) + 500
        happen, gesture_array = wait_for_gesture(480, extra_interactions)

        if happen:
            extra_interactions = []
            if gesture_array[0] == "right" and direction != "x-":
                direction = "x+"
            elif gesture_array[0] == "left" and direction != "x+":
                direction = "x-"
            elif gesture_array[0] == "up" and direction != "y+":
                direction = "y-"
            elif gesture_array[0] == "down" and direction != "y-":
                direction = "y+"
            else:
                print("Gesture no exist", gesture_array, direction)
        elif not happen:
            extra_interactions = gesture_array

        if snake_coords[-1] == food_coord:
            eaten = True
            #lp.LedCtrlXYByCode(food_coord[0], food_coord[1], 0)
            # Re-choose the food spot
            rand_x_temp = random.randint(0, 7)
            rand_y_temp = random.randint(1, 8)
            while [rand_x_temp, rand_y_temp] in snake_coords:
                rand_x_temp = random.randint(0, 7)
                rand_y_temp = random.randint(1, 8)
            food_coord = [rand_x_temp, rand_y_temp]


        if direction == "x+" and snake_coords[-1][0] < 7 and [snake_coords[-1][0] + 1, snake_coords[-1][1]] not in snake_coords: # Right
            did_change_pos = True
            snake_coords.append([snake_coords[-1][0] + 1, snake_coords[-1][1]])
        elif direction == "x-" and snake_coords[-1][0] > 0 and [snake_coords[-1][0] - 1, snake_coords[-1][1]] not in snake_coords: # Left
            did_change_pos = True
            snake_coords.append([snake_coords[-1][0] - 1, snake_coords[-1][1]])
        elif direction == "y+" and snake_coords[-1][1] < 8 and [snake_coords[-1][0], snake_coords[-1][1] + 1] not in snake_coords: # Down
            did_change_pos = True
            snake_coords.append([snake_coords[-1][0], snake_coords[-1][1] + 1])
        elif direction == "y-" and snake_coords[-1][1] > 1 and [snake_coords[-1][0], snake_coords[-1][1] - 1] not in snake_coords: # Up
            did_change_pos = True
            snake_coords.append([snake_coords[-1][0], snake_coords[-1][1] - 1])

        while time.monotonic() * 1000 < end_time - 5: # If there is time left before the next update, wait
            continue

        if did_change_pos:
            if not eaten:
                lp.LedCtrlXYByCode(snake_coords[0][0], snake_coords[0][1], 0)
                snake_coords.pop(0)
        elif not did_change_pos: # If the snake is taking damage
            sad_red_snake = True
            lp.LedCtrlXYByCode(snake_coords[0][0], snake_coords[0][1], 0)
            snake_coords.pop(0)
            if len(snake_coords) > 4:
                lp.LedCtrlXYByCode(snake_coords[0][0], snake_coords[0][1], 0)
                snake_coords.pop(0)

    clear_screen()
    for y in range(1, 9):
        for x in range(8):
            current_num = (y-1) * 8 + x + 1
            print(current_num)
            if current_num > max_score:
                break
            lp.LedCtrlXYByCode(x, y, blue_food)
            time.sleep(0.25)
            lp.LedCtrlXYByCode(x, y, blue_snake)
    time.sleep(2 + max_score/3)
    clear_screen()

clear_screen()

lp.Close()
print("end")