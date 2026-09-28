To allocate tasks for clearing the living room by moving pillows and items off the coffee table and sofa, we need to consider both the skills and mass capacity of each robot. Here's how we can approach this task:

### GENERAL TASK DECOMPOSITION
- **SubTask 1:** Move pillows off the sofa. (Skills Required: GoToObject, PickupObject, PutObject)
- **SubTask 2:** Move items off the coffee table. (Skills Required: GoToObject, PickupObject, PutObject)

### TASK ALLOCATION

#### Available Robots:
1. **Robot 1**: Skills - ['OpenObject', 'CloseObject', 'SwitchOn', 'SwitchOff', 'PickupObject', 'PutObject'], Mass Capacity - 100
2. **Robot 2**: Skills - ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff', 'PickupObject', 'PutObject','DropHandObject','ThrowObject','PushObject','PullObject'], Mass Capacity - 5
3. **Robot 3**: Skills - ['GoToObjec't,'OpenObjec't,'CloseObjec't,'BreakObjec't,'SliceObjec't,'SwitchOn','SwitchOff','PickupObjec't,'PutObjec't,'DropHandObjec't,'ThrowObjec't,'PushObjec't,'PullObje'ct], Mass Capacity - 0.4
4. **Robot 4**: Skills - Same as Robot 3, Mass Capacity - 0.4

#### Objects:
- Pillows have a mass of approximately ~0.7.
- Items on the coffee table vary but are generally light.

### Allocation Strategy:

1. **SubTask 1 (Move Pillows Off Sofa):**
   - Requires skills: `GoToObje'ct`, `PickupObje'ct`, `PutObje'ct`.
   - Suitable Robots: Robot 2 (has all required skills and sufficient mass capacity).

2. **SubTask 2 (Move Items Off Coffee Table):**
   - Requires skills: `GoToObje'ct`, `PickupObje'ct`, `PutObje'ct`.
   - Suitable Robots: Robot 2 (has all required skills and sufficient mass capacity).

### CODE Solution

```python
import threading

def move_pillows_off_sofa(robot):
    # SubTask 1: Move pillows off the sofa
    # Assuming there are two pillows to move
    for _ in range(2):
        # Go to the Pillow on the Sofa.
        GoToObject(robot, 'Pillow')
        # Pick up the Pillow.
        PickupObject(robot, 'Pillow')
        # Go to a designated storage area or corner.
        GoToObject(robot, 'StorageArea')
        # Put the Pillow in the storage area.
        PutObject(robot, 'Pillow', 'StorageArea')

def move_items_off_coffee_table(robot):
    # SubTask 2: Move items off the coffee table
    # Assuming there are two items to move
    for _ in range(2):
        # Go to an item on the CoffeeTable.
        GoToObject(robot, 'Item')
        # Pick up the item.
        PickupObject(robot, 'Item')
        # Go to a designated storage area or corner.
        GoToObject(robot, 'StorageArea')
        # Put the item in the storage area.
        PutObject(robot, 'Item', 'StorageArea')

# Execute SubTask 1 and SubTask 2 in parallel if possible using Robot 2
task1_thread = threading.Thread(target=move_pillows_off_sofa, args=(robots[1],))
task2_thread = threading.Thread(target=move_items_off_coffee_table, args=(robots[1],))

# Start executing SubTask 1 and SubTask 2
task1_thread.start()
task2_thread.start()

# Wait for both SubTask 1 and SubTask 2 to finish
task1_thread.join()
task2_thread.join()

# Task to clear the living room for home training is done
```

### Notes:
- Ensure that each robot knows how to identify "Pillow" and "Item" objects within its environment.
- Adjust repetitions based on actual numbers of pillows and items present.
- The code assumes that Robot 2 is capable of handling both subtasks due to its skill set and mass capacity.