const $ = id => document.getElementById(id);

$('login-form').addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const status = $('login-status');
  status.textContent = 'Entrando…';
  try {
    const resposta = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ usuario: $('usuario').value, senha: $('senha').value }),
    });
    const resultado = await resposta.json().catch(() => null);
    if (resposta.ok && resultado && resultado.sucesso) {
      const parametros = new URLSearchParams(location.search);
      location.href = parametros.get('proximo') || '/';
    } else {
      status.textContent = (resultado && resultado.erro) || 'Usuário ou senha incorretos.';
    }
  } catch (erro) {
    status.textContent = 'Não foi possível conectar ao servidor. Tente novamente.';
  }
});
