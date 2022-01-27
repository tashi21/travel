// If an input has the class "error" and the user clicks on it,
$("input.error").on("focus", function () {
    // Get the id of the input
    const id = `#${$(this).attr("id")}`;

    // Remove the class "error" from the input
    $(id).removeClass("error");

    // Get the name of the error message
    const name = `.error-${id.substring(4)}`;

    // Remove the error message
    $(name).remove();
});
