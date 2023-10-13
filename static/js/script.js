// task started
const sortableListStarted = document.querySelector(".task-list-started");
const itemsStarted = sortableListStarted.querySelectorAll(".item-started");

const sortableList = document.querySelector(".task-list");
const items = sortableList.querySelectorAll(".item");

// task completed
const sortableListDone = document.querySelector(".task-list-done");
const itemsDone = sortableListDone.querySelectorAll(".item-done");

// ---------- TASK STARTED ---------- //
itemsStarted.forEach(item => {
    item.addEventListener("dragstart", () => {
        // Adding dragging class to item after a delay
        setTimeout(() => item.classList.add("dragging-task-started"), 0);
    });
    // Removing dragging class from item on dragend event
    item.addEventListener("dragend", () => item.classList.remove("dragging-task-started"));
});

const initSortableListStarted = (e) => {
    e.preventDefault();
    const draggingItemStarted = sortableListStarted.querySelector(".dragging-task-started");
    //Getting all items except currently dragging and marking array of them
    const siblingsStarted = [...sortableListStarted.querySelectorAll(".item-started:not(.dragging-task-started)")];

    // Finding the sibling after which the dragging item should be placed
    let nextSiblingStarted = siblingsStarted.find(sibling => {
        return e.clientY <= sibling.offsetTop + sibling.offsetHeight / 2;
    });

    // Insert the dragging item before the found sibling
    sortableListStarted.insertBefore(draggingItemStarted, nextSiblingStarted);
}

sortableListStarted.addEventListener("dragover", initSortableListStarted);
sortableListStarted.addEventListener("dragenter", e => e.preventDefault());

// ---------- NORMAL TASKS --------- //
items.forEach(item => {
    item.addEventListener("dragstart", () => {
        // Adding dragging class to item after a delay
        setTimeout(() => item.classList.add("dragging-task"), 0);
    });
    // Removing dragging class from item on dragend event
    item.addEventListener("dragend", () => item.classList.remove("dragging-task"));
});

const initSortableList = (e) => {
    e.preventDefault();
    const draggingItem = sortableList.querySelector(".dragging-task");
    //Getting all items except currently dragging and marking array of them
    const siblings = [...sortableList.querySelectorAll(".item:not(.dragging-task)")];

    // Finding the sibling after which the dragging item should be placed
    let nextSibling = siblings.find(sibling => {
        return e.clientY <= sibling.offsetTop + sibling.offsetHeight / 2;
    });

    // Insert the dragging item before the found sibling
    sortableList.insertBefore(draggingItem, nextSibling);
}

sortableList.addEventListener("dragover", initSortableList);
sortableList.addEventListener("dragenter", e => e.preventDefault());

// ---------- COMPLETED TASKS ---------- //
itemsDone.forEach(item => {
    item.addEventListener("dragstart", () => {
        // Adding dragging class to item after a delay
        setTimeout(() => item.classList.add("dragging-task-done"), 0);
    });
    // Removing dragging class from item on dragend event
    item.addEventListener("dragend", () => item.classList.remove("dragging-task-done"));
});

const initSortableListDone = (e) => {
    e.preventDefault();
    const draggingItemDone = sortableListDone.querySelector(".dragging-task-done");
    //Getting all items except currently dragging and marking array of them
    const siblingsDone = [...sortableListDone.querySelectorAll(".item-done:not(.dragging-task-done)")];

    // Finding the sibling after which the dragging item should be placed
    let nextSiblingDone = siblingsDone.find(sibling => {
        return e.clientY <= sibling.offsetTop + sibling.offsetHeight / 2;
    });

    // Insert the dragging item before the found sibling
    sortableListDone.insertBefore(draggingItemDone, nextSiblingDone);
}

sortableListDone.addEventListener("dragover", initSortableListDone);
sortableListDone.addEventListener("dragenter", e => e.preventDefault());