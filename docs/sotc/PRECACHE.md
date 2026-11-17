# Pre-cache no Linux

No `sotc.ini`, antes de abrir o jogo:

```ini
SOTC_PREFETCH=1
SOTC_ASYNC_PRELOAD=0
SOTC_DRIVER_CACHE=1
```

`SOTC_PREFETCH=1` le os arquivos `.psarc` antes de iniciar o processo do jogo,
em blocos de 4 MiB, com progresso no terminal. Os arquivos menores vem primeiro.
Se houver update, o arquivo do update substitui o de mesmo nome no jogo base.
Nada e modificado no dump.

O limite e o menor entre metade da RAM total e a memoria disponivel menos uma
reserva para o jogo: pelo menos 6 GiB ou um quarto da RAM, o que for maior.
Se os arquivos nao couberem nesse limite, a leitura antecipada e ignorada.
O cache do sistema pode ser recuperado pelo Linux quando outros programas
precisarem de RAM; os dados nao ficam presos na memoria.

`SOTC_ASYNC_PRELOAD=0` termina a criacao dos pipelines ja registrados no cache
durante o carregamento, em vez de continuar esse trabalho enquanto o jogo inicia.
O primeiro encontro com um shader ainda desconhecido pode causar uma pausa;
o cache persistente melhora as proximas visitas e execucoes. Isto nao promete
eliminar todas as pausas de streaming, compilacao ou carga da GPU.

Para pular a leitura dos arquivos, use `SOTC_PREFETCH=0`.
A configuracao `SOTC_MOUSE=0` continua independente e impede a captura do mouse.
