* ============================================================
* Modelos MOSFET genericos LEVEL=1 (Shichman-Hodges)
* ------------------------------------------------------------
* AVISO: NAO sao modelos de fabrica. Nao modelam conducao
* sub-limiar (a regiao de pA onde o neuronio de fato opera),
* nem descasamento, nem dependencia de temperatura realista.
* Uso: comportamento qualitativo e dimensionamento inicial
* apenas. Substituidos pelo PDK SkyWater 130 nm na etapa 1.
* Parametros: valores de livro-texto para um processo generico
* de ~0,35 um, NAO extraidos de silicio.
* ============================================================
.model NMOS NMOS (LEVEL=1 VTO=0.45 KP=120u GAMMA=0.4 PHI=0.7
+ LAMBDA=0.06 TOX=4n CGSO=0.2n CGDO=0.2n CJ=1m CJSW=0.2n)
.model PMOS PMOS (LEVEL=1 VTO=-0.45 KP=45u GAMMA=0.5 PHI=0.7
+ LAMBDA=0.08 TOX=4n CGSO=0.2n CGDO=0.2n CJ=1m CJSW=0.2n)
