function addTodo() {
 var newTodoText = document.getElementById("newTodo").value;
 if (newTodoText) {
 var li = document.createElement("li");
 li.innerHTML = newTodoText + "<button onclick=\"deleteTodo(this)\">Delete</button>";
 document.getElementById("todoList").appendChild(li);
 document.getElementById("newTodo").value = "";
 }
}

function deleteTodo(button) {
 var li = button.parentNode;
 li.parentNode.removeChild(li);
}
