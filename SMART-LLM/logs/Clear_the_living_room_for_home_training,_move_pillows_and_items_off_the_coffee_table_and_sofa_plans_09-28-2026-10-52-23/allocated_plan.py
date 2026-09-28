To clear the living room for home training by moving pillows and items off the coffee table and sofa, we need to allocate tasks to robots based on their skills and mass capacity. Here's how we can approach this task:

### GENERAL TASK DECOMPOSITION
- **SubTask 1:** Move pillows off the sofa. (Skills Required: GoToObject, PickupObject, PutObject)
- **SubTask 2:** Move items off the coffee table. (Skills Required: GoToObject, PickupObject, PutObject)

### TASK ALLOCATION

#### Available Robots:
1. **Robot 1**: Skills - ['OpenObject', 'CloseObject', 'SwitchOn', 'SwitchOff', 'PickupObject', 'PutObject'], Mass Capacity - 100
2. **Robot 2**: Skills - ['GoToObject', 'OpenObject', 'CloseObject', 'BreakObject', 'SliceObject', 'SwitchOn', 'SwitchOff', 'PickupObject', 'PutObject','DropHandObject','ThrowObject','PushObject','PullObject'], Mass Capacity - 5
3. **Robot 3**: Skills - ['GoToObject','OpenObjec't,'CloseObjec't,'BreakObjec't,'SliceObjec't,'SwitchOn','SwitchOff','PickupObjec't,'PutObjec't,'DropHandObjec't,'ThrowObjec't,'PushObjec't,'PullObje'ct], Mass Capacity - 0.4
4. **Robot 4**: Skills - Same as Robot 3, Mass Capacity - 0.4

#### Objects:
- Pillows have a mass of approximately ~0.7.
- Items on the coffee table vary but are generally light.

### Allocation Strategy:

1. **SubTask 1 (Move Pillows Off Sofa):**
   - Requires skills: `GoToObje'ct`, `PickupObje'ct`, `PutObje'ct`.