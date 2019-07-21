function myFunction() {
  var h1 = document.documentElement;
  var att = document.createAttribute("dir");
  att.value = "auto";
  h1.setAttributeNode(att);
};
window.onload = function() {
  myFunction();
}