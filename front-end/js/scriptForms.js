// Pega o formulário pelo ID
const form = document.getElementById('forms-pesquisa');

form.addEventListener('submit', function(event) {
  event.preventDefault(); // Evita o envio padrão do formulário

  // Pega os valores dos inputs
  const palavraChave = document.getElementById('palavra-chave').value;
  

  //Testando se chega 
  console.log('Palavra-chave:', palavraChave);

  
});





