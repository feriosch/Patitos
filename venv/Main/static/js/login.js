function validateForm() {
  var x = document.forms["login_form"]["usuario"].value;
  if (x == "") {
      var popup = document.getElementById("usuario_vacio");
      popup.classList.toggle("show");
      return false;
  }
}
