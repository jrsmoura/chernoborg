# Relatório de Acurácia — Assistente Virtual IESB

**Data:** 28/06/2026  
**Modelo:** Claude Haiku 4.5 via AWS Bedrock  
**Embeddings:** Amazon Titan Embeddings v2 (1024 dims)  
**Índice:** FAISS IndexFlatIP — 99 chunks de 64 páginas

---

## Resultado Geral

| Métrica | Valor |
|---|---|
| Total de perguntas | 38 |
| PASS | 33 |
| FAIL | 5 |
| **Acurácia geral** | **86.8%** |
| Atividades Complementares (AC) | 13/18 — 72% |
| Extensão Curricularizada (EXT) | 20/20 — 100% |

---

## Tabela de Resultados

| ID | Pergunta | Status | Keywords |
|---|---|:---:|:---:|
| AC-01 | O que são atividades complementares? | ✅ PASS | 4/4 |
| AC-02 | Como faço para comprovar uma atividade complementar externa? | ✅ PASS | 4/4 |
| AC-03 | Quanto tempo leva para minha atividade complementar ser validada? | ❌ FAIL | 0/3 |
| AC-04 | Quais são os grupos de atividades complementares do IESB? | ❌ FAIL | 1/5 |
| AC-05 | Quais atividades fazem parte do Grupo I de atividades complementares? | ❌ FAIL | 0/4 |
| AC-06 | Quais atividades fazem parte do Grupo II de atividades complementares? | ❌ FAIL | 0/3 |
| AC-07 | O que são as atividades do Grupo III de atividades complementares? | ✅ PASS | 4/4 |
| AC-08 | O que são as atividades do Grupo IV de atividades complementares? | ❌ FAIL | 1/4 |
| AC-09 | Quantas horas valem por produção de artigo científico individual? | ✅ PASS | 3/3 |
| AC-10 | Qual a carga horária máxima que posso validar por participação em congressos e palestras? | ✅ PASS | 3/3 |
| AC-11 | Quais são as responsabilidades dos estudantes em relação às atividades complementares? | ✅ PASS | 4/4 |
| AC-12 | Qual o tamanho máximo do arquivo para envio de atividade complementar no Aluno Online? | ✅ PASS | 2/3 |
| AC-13 | Até quando devo entregar as atividades complementares? | ✅ PASS | 3/3 |
| AC-14 | Sou formando, qual o prazo para minhas atividades complementares? | ✅ PASS | 3/4 |
| AC-15 | Passo a passo: como enviar minha atividade complementar no Aluno Online? | ✅ PASS | 3/4 |
| AC-16 | Entrei no IESB por transferência. Posso validar atividades da minha instituição anterior? | ✅ PASS | 4/4 |
| AC-17 | Como verificar se minha solicitação de atividade complementar foi deferida ou indeferida? | ✅ PASS | 4/4 |
| AC-18 | Onde encontro os registros das minhas atividades complementares validadas? | ✅ PASS | 2/4 |
| EXT-01 | O que é a extensão curricularizada? | ✅ PASS | 4/4 |
| EXT-02 | Qual resolução do MEC regulamenta a extensão curricularizada? | ✅ PASS | 4/4 |
| EXT-03 | Qual percentual mínimo da carga horária do curso deve ser dedicado à extensão? | ✅ PASS | 4/4 |
| EXT-04 | O que são os ODS? | ✅ PASS | 3/4 |
| EXT-05 | Quantos ODS existem e o que é a Agenda 2030? | ✅ PASS | 3/4 |
| EXT-06 | Quais são as trilhas de aprendizagem disponíveis na extensão do IESB? | ✅ PASS | 4/4 |
| EXT-07 | O que é a Trilha Comunitária? | ✅ PASS | 5/5 |
| EXT-08 | O que é a Trilha de Empreendedorismo? | ✅ PASS | 4/4 |
| EXT-09 | Qual é o objetivo geral da disciplina de extensão? | ✅ PASS | 5/5 |
| EXT-10 | O que é o tema norteador da extensão curricularizada? | ✅ PASS | 4/4 |
| EXT-11 | O que é o Blackboard e para que serve na disciplina de extensão? | ✅ PASS | 4/4 |
| EXT-12 | O que é a DreamShaper? | ✅ PASS | 3/4 |
| EXT-13 | Como funciona a avaliação P1 da disciplina de extensão? | ✅ PASS | 4/5 |
| EXT-14 | O que é o Vídeo Pitch e qual a duração máxima? | ✅ PASS | 4/4 |
| EXT-15 | O que é a PS da disciplina de extensão e como ela substitui a P1? | ✅ PASS | 5/5 |
| EXT-16 | O que é o relatório analítico e quando devo entregá-lo? | ✅ PASS | 4/4 |
| EXT-17 | Sou obrigado a fazer a disciplina de extensão? | ✅ PASS | 5/5 |
| EXT-18 | Como sei em qual trilha fui alocado se não escolhi a tempo? | ✅ PASS | 4/5 |
| EXT-19 | Posso alterar a minha trilha de extensão depois de alocado? | ✅ PASS | 4/4 |
| EXT-20 | Como verifico se estou matriculado na disciplina de extensão? | ✅ PASS | 4/4 |

---

## Análise das Falhas

Total de falhas: **5** — todas no Guia de Atividades Complementares.

### Causa Raiz

As páginas 9–11 do Guia de Atividades Complementares contêm tabelas de 4 colunas
(Grupo, Tipo de Atividade, Critério de Validação, Documento Comprobatório).
`pdftotext -layout` intercala as linhas das colunas ao extrair, produzindo texto
embaralhado que degrada a qualidade do embedding e compromete o retrieval.

### Recomendação

Aplicar `GeminiVisionExtractor` especificamente nas páginas 9–11 do Guia de
Atividades Complementares para obter transcrição na ordem correta de leitura.

### Detalhamento por falha

**AC-03** — Quanto tempo leva para minha atividade complementar ser validada?

- Keywords esperados: `30 dias úteis, validação, lançamento`
- Encontrados: 0/3
- Trecho da resposta: _Não encontrei nos guias um prazo específico informando quanto tempo leva para validar sua atividade complementar após a_

**AC-04** — Quais são os grupos de atividades complementares do IESB?

- Keywords esperados: `quatro grupos, Grupo I, Grupo II, Grupo III, Grupo IV`
- Encontrados: 1/5
- Trecho da resposta: _Com base nos guias oficiais, as atividades complementares do IESB estão divididas em **4 grupos distintos**:  1. **Grupo_

**AC-05** — Quais atividades fazem parte do Grupo I de atividades complementares?

- Keywords esperados: `cursos de extensão, palestras, eventos, congressos`
- Encontrados: 0/4
- Trecho da resposta: _Com base no guia, o **Grupo I** é dedicado a **Qualificação Profissional**.   De acordo com a definição apresentada:  **_

**AC-06** — Quais atividades fazem parte do Grupo II de atividades complementares?

- Keywords esperados: `artigo científico, publicação, iniciação científica`
- Encontrados: 0/3
- Trecho da resposta: _De acordo com o guia oficial, o **Grupo II - Produção Científica** abrange atividades relativas à produção do conhecimen_

**AC-08** — O que são as atividades do Grupo IV de atividades complementares?

- Keywords esperados: `monitoria, estágio, vivência profissional, Grupo IV`
- Encontrados: 1/4
- Trecho da resposta: _Infelizmente, **a informação específica sobre o Grupo IV não foi encontrada nos trechos retornados dos guias**.   Porém,_

---

## Perguntas e Respostas por Guia

### Guia de Atividades Complementares

**Arquivo:** `Guia_de_Atividades_Complementares_Atualizado_10_02_2026.pdf`  

**Páginas indexadas:** 2–24 (exceto p1 — capa; p23 — formulário em branco)  

**Resultado:** 13/18 perguntas respondidas corretamente (72%)

#### ✅ AC-01 — O que são atividades complementares?

## O que são Atividades Complementares?

As **atividades complementares** são **componentes curriculares obrigatórios** dos cursos de graduação que visam enriquecer o processo de ensino e aprendizagem.

Elas são atividades que permitem o reconhecimento, por avaliação, de:

- Habilidades
- Conhecimentos
- Competências do aluno

Essas competências podem ter sido adquiridas **dentro ou fora do ambiente escolar**, incluindo estudos independentes, atividades transversais e opcionais, com especial foco nas relações com o mundo do trabalho e ações de extensão junto à comunidade.

**Na prática**, as atividades complementares permitem ao estudante realizar trabalhos práticos ligados à profissão escolhida desde o primeiro semestre do curso. Podem ser:

- **Oferecidas pelo IESB**, conforme planejamento da coordenação do curso
- **Realizadas externamente**, por interesse do estudante

Alguns exemplos incluem: extensão, iniciação científica, qualificação profissional, trabalho voluntário, monitoria e outras atividades que enriqueçam o perfil profissional.

---

**Fonte:** Guia de Atividades Complementares Atualizado 10 02 2026, pp. 2-3

> Keywords avaliados: `atividades complementares, práticos, profissão, primeiro semestre` — 4/4 encontrados

---

#### ✅ AC-02 — Como faço para comprovar uma atividade complementar externa?

Com base nos guias oficiais do IESB, aqui está o passo a passo para comprovar uma atividade complementar externa:

## Procedimento

**1. Reúna o documento comprobatório**

- **Certificado de participação** (ideal) — emitido pela instituição/evento
- OU — se não tiver certificado, reúna outros comprovantes: fotos, ingressos, folders, etc.

**2. Acesse a Plataforma Aluno Online**

- Menu **Serviços Acadêmicos** > **Atividades Complementares** > **Requerimento de Atividade Complementar** > **Abrir Solicitação**

**3. Envie o arquivo**

- Poste o documento comprobatório
- **Limite**: máximo 1 arquivo por solicitação, com tamanho máximo de **2MB**
- Se precisar enviar vários arquivos, faça múltiplas solicitações

**4. Se não tiver certificado**

- Preencha o **Relatório de Atividades Complementares (RAC)** com as informações detalhadas da atividade
- O formulário está disponível em: Aluno Online > Menu Serviços Acadêmicos > Atividades Complementares > **Material de Apoio**

## Prazos

A solicitação será analisada, validada e lançada em até **30 dias úteis**. Você pode acompanhar o andamento em: Aluno Online > Menu Serviços Acadêmicos > Atividades Complementares > **Atividades Cadastradas**.

(Fonte: Guia de Atividades Complementares Atualizado 10/02/2026, p. 3 e 12)

> Keywords avaliados: `Aluno Online, Requerimento, documento, comprobatório` — 4/4 encontrados

---

#### ❌ AC-03 — Quanto tempo leva para minha atividade complementar ser validada?

Não encontrei nos guias um prazo específico informando quanto tempo leva para validar sua atividade complementar após a entrega.

O que o guia menciona é:

- **Prazo de entrega**: Você deve entregar suas atividades complementares conforme o calendário acadêmico disponível em <http://apps.iesb.br/sistemasAcademicos/calendario>. Este é um prazo importante que você deve cumprir para que suas atividades sejam validadas sem contratempos.

- **Para formandos**: Se você é provável formando, deve entregar todas as atividades complementares até o último dia do período letivo de integração do curso.

Para saber quanto tempo a coordenação leva para validar sua atividade após entrega, recomendo que você entre em contato com a coordenação de Atividades Complementares pelo e-mail **<ativ.complementar@iesb.br>**.

> Keywords avaliados: `30 dias úteis, validação, lançamento` — 0/3 encontrados

---

#### ❌ AC-04 — Quais são os grupos de atividades complementares do IESB?

Com base nos guias oficiais, as atividades complementares do IESB estão divididas em **4 grupos distintos**:

1. **Grupo I – Qualificação Profissional**: atividades relacionadas à formação profissional que visam à aquisição de conhecimentos, habilidades e atitudes exigidas para o exercício profissional.

De acordo com os trechos consultados, há menção a outros grupos além do Grupo I, mas a descrição completa dos grupos II, III e IV não foi totalmente capturada. O guia menciona ainda atividades de **extensão, iniciação científica, atividades de qualificação profissional, trabalho voluntário e monitoria**.

Para conhecer a descrição completa de todos os 4 grupos e exemplos específicos de cada um, recomendo acessar o **Guia de Atividades Complementares Atualizado** na Plataforma Aluno Online ou entrar em contato com a coordenação pelo e-mail **<ativ.complementar@iesb.br>**.

(Fonte: Guia de Atividades Complementares Atualizado 10.02.2026, p. 4)

> Keywords avaliados: `quatro grupos, Grupo I, Grupo II, Grupo III, Grupo IV` — 1/5 encontrados

---

#### ❌ AC-05 — Quais atividades fazem parte do Grupo I de atividades complementares?

Com base no guia, o **Grupo I** é dedicado a **Qualificação Profissional**.

De acordo com a definição apresentada:

**Grupo I – Qualificação Profissional** são atividades relacionadas à formação profissional que visam à aquisição de conhecimentos, habilidades e atitudes exigidas para o exercício profissional.

O guia menciona que "dentre as atividades de qualificação profissional o (a) estudante poderá validar:" mas os trechos retornados não detalham a lista completa de atividades específicas do Grupo I.

Para conhecer a **lista detalhada de atividades que fazem parte do Grupo I**, recomendo que você consulte a página completa do Guia de Atividades Complementares ou entre em contato com a coordenação pelo e-mail **<ativ.complementar@iesb.br>**.

(Fonte: Guia de Atividades Complementares Atualizado 10 02 2026, p. 4)

> Keywords avaliados: `cursos de extensão, palestras, eventos, congressos` — 0/4 encontrados

---

#### ❌ AC-06 — Quais atividades fazem parte do Grupo II de atividades complementares?

De acordo com o guia oficial, o **Grupo II - Produção Científica** abrange atividades relativas à produção do conhecimento realizadas por estudantes, supervisionadas por docentes do Centro Universitário IESB.

São atividades relacionadas ao conhecimento científico produzido no Centro Universitário IESB, com foco na divulgação do conhecimento e das pesquisas. O objetivo é desenvolver as profissões e aproximar a instituição da sociedade, propondo alternativas e soluções para problemáticas cotidianas, auxiliando no desenvolvimento sustentável e socioeconômico.

Para conhecer as atividades específicas listadas dentro do Grupo II, recomendo consultar a página completa do guia ou entrar em contato com a coordenação de seu curso, pois o trecho retornado introduz a categoria mas não detalha todas as atividades específicas.

**(Fonte: Guia de Atividades Complementares Atualizado 10 02 2026, p. 5)**

Se precisar de mais informações detalhadas, entre em contato com <ativ.complementar@iesb.br>.

> Keywords avaliados: `artigo científico, publicação, iniciação científica` — 0/3 encontrados

---

#### ✅ AC-07 — O que são as atividades do Grupo III de atividades complementares?

Perfeito! Agora tenho todas as informações necessárias para responder.

## O Grupo III de Atividades Complementares

O **Grupo III – Atividades Humanísticas** são atividades que visam desenvolver habilidades interpessoais requeridas pelo mercado de trabalho, como também despertar no egresso do Centro Universitário IESB uma sensibilidade para questões sociais emergentes da sociedade contemporânea.

As atividades que o estudante pode validar no Grupo III são:

✓ **Trabalho voluntário** em instituições sem fins lucrativos  
✓ **Participação em projetos sociais** vinculados às instituições que tenham o certificado de entidade beneficente de assistência social  
✓ **Participação nos projetos da Cátedra UNESCO** desenvolvidos pelo Centro Universitário IESB  
✓ **Participação em projetos de extensão** desenvolvidos pelo Centro Universitário IESB

**Critérios de validação:**

- **Atividades de cunho social**: até **50 horas máximo**, validadas por hora, mediante declaração da instituição
- **Participação em pesquisas da CPA**: semestre equivale a **5 horas**, comprovado por comprovante de participação

(Fonte: Guia de Atividades Complementares Atualizado 10 02 2026, pp. 6-7)

> Keywords avaliados: `voluntário, social, humanísticas, UNESCO` — 4/4 encontrados

---

#### ❌ AC-08 — O que são as atividades do Grupo IV de atividades complementares?

Infelizmente, **a informação específica sobre o Grupo IV não foi encontrada nos trechos retornados dos guias**.

Porém, segundo os guias, o IESB classifica as atividades complementares em **quatro grupos distintos**, sendo que o Grupo I foi mencionado (Qualificação Profissional). Para obter a definição completa do Grupo IV e de todos os grupos, recomendo:

1. **Consultar o Guia de Atividades Complementares completo** no portal Aluno Online, especialmente as páginas 4 e 5
2. **Entrar em contato com a coordenação de Atividades Complementares** pelo e-mail: **<ativ.complementar@iesb.br>**

Posso ajudá-lo com outras informações sobre atividades complementares que estejam nos guias, como prazos, procedimentos de validação ou carga horária exigida. O que mais gostaria de saber?

> Keywords avaliados: `monitoria, estágio, vivência profissional, Grupo IV` — 1/4 encontrados

---

#### ✅ AC-09 — Quantas horas valem por produção de artigo científico individual?

A produção de **artigo científico individual** vale **20 horas**.

No entanto, é importante observar que existem diferentes modalidades:

- **Artigo científico individual (não publicado)**: 20 horas
- **Artigo científico individual publicado** em revista científica, site, anais de eventos e/ou livro: 30 horas

Portanto, se seu artigo for publicado, você pode validar até 30 horas.

(Fonte: Guia de Atividades Complementares Atualizado 10 02 2026, p. 10)

> Keywords avaliados: `20 horas, artigo, individual` — 3/3 encontrados

---

#### ✅ AC-10 — Qual a carga horária máxima que posso validar por participação em congressos e palestras?

Com base no guia oficial, a **carga horária máxima que você pode validar por participação em congressos, palestras, conferências, debates e seminários é de até 30 horas por evento**.

A validação é feita por hora, e você precisará apresentar um **certificado de participação** como comprovante.

(Fonte: Guia de Atividades Complementares Atualizado 10/02/2026, p. 9)

> Keywords avaliados: `30 horas, evento, certificado` — 3/3 encontrados

---

#### ✅ AC-11 — Quais são as responsabilidades dos estudantes em relação às atividades complementares?

Com base no Guia de Atividades Complementares, as responsabilidades dos estudantes em relação às atividades complementares são:

## Responsabilidades Principais

**A) Comparecer às atividades inscritas**
Você deve estar presente nas atividades em que realizou a inscrição.

**B) Manter-se atualizado**
Estar sempre informado sobre as atividades complementares disponíveis.

**C) Postar as atividades externas com documentos comprobatórios**
Você deve submeter as atividades externas realizadas por meio da **Plataforma Aluno Online > Serviços Acadêmicos > Atividades Complementares > Requerimento de Atividade Complementar > Abrir Solicitação**, acompanhadas dos devidos documentos que comprovem a participação.

### Observações importantes sobre o envio de documentos

- Cada solicitação permite o envio de **apenas 1 arquivo**
- O arquivo deve ter **no máximo 2MB**
- Se precisar enviar mais arquivos, deve fazer uma **nova solicitação** para cada um
- Se o arquivo ultrapassar 2MB, você deve reduzi-lo antes de enviar

Caso não consiga o certificado de participação, você pode utilizar outros comprovantes como fotos, ingressos ou folders, preenchendo o **Relatório de Atividades Complementares (RAC)**, disponível na seção Material de Apoio no Aluno Online.

(Fonte: Guia de Atividades Complementares Atualizado 10 02 2026, p. 12 e 3)

> Keywords avaliados: `comparecer, comprovantes, Aluno Online, responsabilidades` — 4/4 encontrados

---

#### ✅ AC-12 — Qual o tamanho máximo do arquivo para envio de atividade complementar no Aluno Online?

O tamanho máximo do arquivo para envio de atividade complementar no Aluno Online é de **2MB**.

Importante: Cada solicitação permite o envio de apenas um arquivo. Se você precisar enviar mais arquivos, deverá realizar uma nova solicitação. Em caso de arquivos superiores a 2MB, será necessário reduzi-los antes do envio.

(Fonte: Guia de Atividades Complementares Atualizado 10 02 2026, p. 12)

> Keywords avaliados: `2MB, arquivo, redução` — 2/3 encontrados

---

#### ✅ AC-13 — Até quando devo entregar as atividades complementares?

O prazo para entregar as atividades complementares é estabelecido conforme o **calendário acadêmico** do IESB, disponível em: <http://apps.iesb.br/sistemasAcademicos/calendario>

**⚠️ Atenção especial se você é formando:**
Se você é um provável formando, todas as atividades complementares **devem ser entregues até o último dia do período letivo da integralização do seu curso**, pois são componentes curriculares obrigatórios para conclusão do curso e participação na colação de grau.

**Importante:** Cumprir os prazos é fundamental para que suas atividades sejam validadas sem contratempos. Caso envie documentação, o prazo de análise e validação é de até 30 dias úteis.

Para confirmar a data exata do seu deadline, consulte o calendário acadêmico no link acima ou entre em contato com a coordenação de atividades complementares em: **<ativ.complementar@iesb.br>**

(Fonte: Guia de Atividades Complementares Atualizado 10 02 2026, p. 13)

> Keywords avaliados: `calendário acadêmico, prazo, entrega` — 3/3 encontrados

---

#### ✅ AC-14 — Sou formando, qual o prazo para minhas atividades complementares?

Para você, como **formando**, há um prazo especial:

**Você deve entregar todas as atividades complementares até o último dia do período letivo da integralização do seu curso.**

As atividades complementares são componentes curriculares obrigatórios para a conclusão do seu curso e para a participação na colação de grau. Portanto, é fundamental que você respeite este prazo.

Além disso, lembre-se que:

- O prazo de análise, validação e lançamento das atividades é de até **30 dias úteis** após o envio
- Você pode acompanhar o status das suas atividades no Aluno Online > Menu Serviços Acadêmicos > Atividades Complementares > Atividades Cadastradas
- O calendário acadêmico exato está disponível em: <http://apps.iesb.br/sistemasAcademicos/calendario>

(Fonte: Guia de Atividades Complementares Atualizado 10 02 2026, p. 13)

> Keywords avaliados: `formandos, último dia, período letivo, colação` — 3/4 encontrados

---

#### ✅ AC-15 — Passo a passo: como enviar minha atividade complementar no Aluno Online?

Ótimo! Aqui está o passo a passo para enviar sua atividade complementar no Aluno Online:

## **Passo a Passo para Enviar Atividades Complementares**

**1º Passo**
Acesse a plataforma Aluno Online em **aonline.iesb.br**

**2º Passo**
Na plataforma, acesse: **Serviços Acadêmicos > Atividades Complementares > Requerimento de Atividade Complementar > Abrir Solicitação**

**3º Passo**
Selecione o arquivo com o documento comprobatório da atividade que realizou

**4º Passo**
Confira o serviço solicitado

**5º Passo**
Clique em **Enviar**

### **Pontos Importantes:**

⚠️ **Cada solicitação permite o envio de apenas UM arquivo**, com tamanho máximo de **2MB**. Se precisar enviar mais arquivos, realize uma **nova solicitação**.

⚠️ **Respeite os prazos** estabelecidos no calendário acadêmico (disponível em: <http://apps.iesb.br/sistemasAcademicos/calendario>)

⚠️ **Formandos**: entreguem todas as atividades complementares até o **último dia do período letivo** de conclusão do curso.

---

**Fonte:** Guia de Atividades Complementares Atualizado 10/02/2026, pp. 12-13

> Keywords avaliados: `Aluno Online, matrícula, Serviços Acadêmicos, solicitação` — 3/4 encontrados

---

#### ✅ AC-16 — Entrei no IESB por transferência. Posso validar atividades da minha instituição anterior?

Sim! Você pode validar atividades realizadas na sua instituição anterior. Aqui estão os detalhes:

## Para Atividades Complementares

Os estudantes transferidos podem validar as atividades complementares realizadas na IES de origem. Para isso, você deve:

- Enviar via Plataforma Aluno Online os documentos que comprovem a carga horária integralizada na IES de origem, para registro no seu histórico.

**Limite importante:** O aproveitamento será de até **50% da carga horária total de atividades complementares** exigida pelo seu curso.

## Para Disciplinas

Se você ingressou com Diploma de Curso Superior (DCS), também pode validar disciplinas cursadas em outras graduações que não sejam equivalentes na matriz curricular do seu curso no IESB. Nesse caso:

- Você deve submeter o histórico escolar e os planos de ensino das disciplinas à coordenação do seu curso para análise.
- O aproveitamento será de até 50% da carga horária total de atividades complementares.

**Importante:** Atividades realizadas em período anterior ao ingresso no IESB geralmente não são validadas, **com exceção para alunos ingressantes por transferência** — é exatamente o seu caso!

Se tiver dúvidas sobre quais documentos enviar ou como proceder, entre em contato com a coordenação do seu curso ou com <ativ.complementar@iesb.br>.

(Fonte: Guia de Atividades Complementares Atualizado 10 02 2026, pp. 12, 20-21)

> Keywords avaliados: `transferência, IES de origem, validar, transferidos` — 4/4 encontrados

---

#### ✅ AC-17 — Como verificar se minha solicitação de atividade complementar foi deferida ou indeferida?

Para verificar se sua solicitação de atividade complementar foi **deferida ou indeferida**, siga estes passos no **Aluno Online**:

## Passos

1. Acesse o menu **Requerimento de Atividades Complementares**

2. Confira o status da sua solicitação

3. **Se a solicitação foi indeferida**: clique em **Visualizar** para verificar o motivo da negação

## Importante

- Você pode acompanhar o lançamento das horas via **Aluno Online > Menu Serviços Acadêmicos > Atividades Complementares > Atividades Cadastradas**
- A solicitação deve ser analisada, validada e lançada em um prazo de **até 30 dias úteis**
- Em caso de dúvidas sobre uma solicitação indeferida, entre em contato pelo e-mail **<ativ.complementar@iesb.br>**

(Fonte: Guia de Atividades Complementares Atualizado 10 02 2026, p. 18)

> Keywords avaliados: `Aluno Online, indeferida, verificar, solicitação` — 4/4 encontrados

---

#### ✅ AC-18 — Onde encontro os registros das minhas atividades complementares validadas?

Para encontrar os registros das suas atividades complementares validadas, siga estes passos no **Aluno Online**:

**1º Passo:** Clique no menu **Serviços Acadêmicos**

**2º Passo:** Clique no ícone **Atividades Complementares**

Neste local você conseguirá conferir todas as atividades validadas e lançadas.

**Observação:** Se você deseja conferir as _solicitaações_ que já enviou (ainda em análise), acesse o menu **Requerimento de Atividades Complementares** no mesmo caminho.

(Fonte: Guia de Atividades Complementares Atualizado 10 02 2026, p. 19)

> Keywords avaliados: `Aluno Online, Atividades Concluídas, carga horária, registros` — 2/4 encontrados

---

### Guia da Extensão Curricularizada

**Arquivo:** `Guia_de_Curricularização_da_Extensao_vf.pdf`  

**Páginas indexadas:** 1–45 (exceto p21–23 e p46–49 — apenas cabeçalho + número)  

**Resultado:** 20/20 perguntas respondidas corretamente (100%)

#### ✅ EXT-01 — O que é a extensão curricularizada?

A **Extensão Curricularizada** é o processo de integrar as atividades de extensão ao currículo de graduação, tornando essas atividades **obrigatórias e componentes da carga horária do curso**.

## Principais características

- **Exigência legal**: A Resolução nº 7/2018 do Ministério da Educação (MEC) estabelece que no mínimo **10% da carga horária dos cursos de graduação** devem ser dedicados a atividades de extensão.

- **No IESB**: Todos os cursos de graduação atendem a essa resolução, garantindo que as atividades extensionistas sejam incorporadas ao percurso acadêmico dos estudantes.

- **Objetivo**: A extensão universitária é entendida como um processo **educativo, cultural e científico** que articula ensino e pesquisa, promovendo uma relação transformadora entre a universidade e a sociedade. As atividades são planejadas para atender às demandas da sociedade, enquanto proporcionam ao estudante uma vivência prática e significativa.

Em resumo, a Extensão Curricularizada reforça o compromisso do IESB com a formação integral dos alunos, conectando ensino, pesquisa e comunidade.

(Fonte: Guia de Curricularização da Extensão, p. 11)

> Keywords avaliados: `extensão curricularizada, currículo, obrigatórias, carga horária` — 4/4 encontrados

---

#### ✅ EXT-02 — Qual resolução do MEC regulamenta a extensão curricularizada?

A extensão curricularizada é regulamentada pela **Resolução nº 7/2018 do Ministério da Educação (MEC)**, que estabelece que, no mínimo, **10% da carga horária dos cursos de graduação** devem ser dedicados a atividades de extensão.

Todos os cursos de graduação do IESB estão em conformidade com essa resolução, garantindo que as atividades extensionistas sejam incorporadas ao percurso acadêmico dos estudantes como componentes obrigatórios.

(Fonte: Guia de Curricularização da Extensão, p. 11)

> Keywords avaliados: `Resolução, 7/2018, MEC, 10%` — 4/4 encontrados

---

#### ✅ EXT-03 — Qual percentual mínimo da carga horária do curso deve ser dedicado à extensão?

De acordo com a regulamentação, **o mínimo de 10% da carga horária total do curso de graduação deve ser dedicado a atividades de extensão**.

Essa exigência está estabelecida pela Resolução nº 7/2018 do Ministério da Educação (MEC) e todos os cursos de graduação do IESB estão alinhados com essa norma. As atividades de extensão são obrigatórias e integram a matriz curricular, garantindo que você tenha uma formação integral que conecta ensino, pesquisa e comunidade.

(Fonte: Guia de Extensão Curricularizada, p. 11)

> Keywords avaliados: `10%, mínimo, carga horária, extensão` — 4/4 encontrados

---

#### ✅ EXT-04 — O que são os ODS?

Os ODS (Objetivos de Desenvolvimento Sustentável) são uma agenda global estabelecida pela ONU com 17 objetivos para transformar o mundo até 2030, abordando temas como erradicação da pobreza, saúde, educação, igualdade, energia limpa, trabalho digno, inovação, entre outros.

No contexto do IESB, os ODS são frequentemente mencionados nas trilhas de Extensão Curricularizada e Atividades Complementares, pois muitos projetos e atividades são alinhados a esses objetivos globais.

Porém, para informações específicas sobre como os ODS se relacionam com suas atividades complementares ou extensão no IESB, deixa eu consultar os guias oficiais para trazer informações mais precisas e relevantes ao seu contexto acadêmico.

Você tem alguma dúvida específica sobre como os ODS se relacionam com as atividades complementares ou extensão curricularizada que você está desenvolvendo?

> Keywords avaliados: `Objetivos de Desenvolvimento Sustentável, ONU, 17, Agenda 2030` — 3/4 encontrados

---

#### ✅ EXT-05 — Quantos ODS existem e o que é a Agenda 2030?

Ótima pergunta! Essas são informações gerais sobre os ODS e a Agenda 2030, que não estão especificamente ligadas às regras de Extensão Curricularizada e Atividades Complementares do IESB.

**Respondendo brevemente:**

Os **ODS (Objetivos de Desenvolvimento Sustentável)** são **17 objetivos globais** estabelecidos pela ONU como parte da **Agenda 2030**.

A **Agenda 2030** é um plano de ação adotado por 193 países em 2015, que busca erradicar a pobreza, proteger o planeta e promover a paz e a prosperidade até 2030. Os 17 ODS são:

1. Erradicação da pobreza
2. Fome zero e agricultura sustentável
3. Saúde e bem-estar
4. Educação de qualidade
5. Igualdade de gênero
6. Água potável e saneamento
7. Energia limpa e acessível
8. Trabalho decente e crescimento econômico
9. Indústria, inovação e infraestrutura
10. Redução das desigualdades
11. Cidades e comunidades sustentáveis
12. Consumo e produção responsáveis
13. Ação climática
14. Vida na água
15. Vida terrestre
16. Paz, justiça e instituições eficazes
17. Parcerias e meios de implementação

---

**Observação importante:** Se sua dúvida está relacionada aos **ODS no contexto das trilhas de Extensão Curricularizada ou Atividades Complementares do IESB**, posso buscar nos guias oficiais como os ODS estão integrados nessas atividades. Avise!

> Keywords avaliados: `17, Agenda 2030, Estados-membros, 2015` — 3/4 encontrados

---

#### ✅ EXT-06 — Quais são as trilhas de aprendizagem disponíveis na extensão do IESB?

O IESB oferece **quatro trilhas temáticas** de extensão para que você escolha a que melhor se alinhe aos seus interesses e formação:

## As Trilhas de Extensão são

1. **Trilha de Empreendedorismo**: Focada na capacitação para desenvolver iniciativas empreendedoras que impactem positivamente a comunidade. Inclui elaboração de planos de negócios, mentorias com empreendedores experientes e projetos voltados para desenvolvimento econômico e inovação.

2. **Trilha de Inovação e Criatividade**: Ideal para quem deseja usar a criatividade como ferramenta de impacto social. Utiliza a metodologia de Design Thinking e desenvolve habilidades como empatia, ideação e prototipagem para resolver problemas de forma inovadora.

3. **Trilha Comunitária**: Incentiva atuação direta nas comunidades, promovendo inclusão social e sustentabilidade. Envolve intervenção em comunidades carentes, ações sociais e programas de voluntariado.

4. **Trilha de Pesquisa**: Focada em pesquisa científica, com atividades como publicação e apresentação de artigos, parcerias com universidades e centros de pesquisa. Desenvolve habilidades de investigação, argumentação e escrita científica.

Todos os projetos de extensão no IESB são alinhados aos **Objetivos de Desenvolvimento Sustentável (ODS)** das Nações Unidas.

**Fonte:** Guia de Curricularização da Extensão, p. 14-18

> Keywords avaliados: `Comunitária, Empreendedorismo, Inovação, Pesquisa` — 4/4 encontrados

---

#### ✅ EXT-07 — O que é a Trilha Comunitária?

A **Trilha Comunitária** tem como objetivo principal conectar os estudantes diretamente com ações sociais e comunitárias, incentivando o engajamento em projetos voltados para inclusão social, sustentabilidade e desenvolvimento local.

**Objetivos:**

- Atuar junto a comunidades carentes e grupos vulneráveis
- Promover impacto positivo por meio de ações voluntárias e educativas

**Exemplos de projetos:**

- Intervenções sociais e comunitárias que promovem mudanças locais significativas
- Desenvolvimento de programas de voluntariado
- Promoção da inclusão social e acesso a direitos básicos (educação, saúde)
- Sustentabilidade e meio ambiente, com foco em preservação e uso consciente de recursos

**Competências desenvolvidas:**
Ao participar dessa trilha, você desenvolve habilidades de lideran­ça, trabalho em equipe e empatia, além de compreender melhor as realidades sociais e desafios das comunidades. Essa experiência favorece crescimento pessoal, aprimoramento acadêmico e profissional.

(Fonte: Guia de Curricularização da Extensão, pp. 14-15)

> Keywords avaliados: `Comunitária, social, inclusão, comunidades, voluntárias` — 5/5 encontrados

---

#### ✅ EXT-08 — O que é a Trilha de Empreendedorismo?

A **Trilha de Empreendedorismo** é voltada para estudantes que desejam desenvolver iniciativas inovadoras e sustentáveis, contribuindo para o fortalecimento da economia e o impacto social positivo.

O foco dessa trilha é **capacitar os estudantes a identificar oportunidades, estruturar ideias e transformar conceitos em projetos viáveis e escaláveis.**

**As atividades incluem:**

- Criação de modelos de negócios inovadores, com base em demandas reais da sociedade
- Desenvolvimento de startups e iniciativas de impacto social, promovendo soluções escaláveis
- Participação em mentorias e workshops com especialistas, fortalecendo o aprendizado prático
- Capacitação em gestão, marketing, finanças e inovação, preparando os estudantes para o mercado

A trilha incentiva especialmente a criação de **negócios de impacto social**, que combinam sustentabilidade financeira com benefícios diretos para comunidades e grupos vulneráveis. O objetivo é que os estudantes adquiram habilidades de gestão, criatividade e visão estratégica, fundamentais para qualquer profissional que deseja empreender ou inovar dentro do seu campo de atuação.

(Fonte: Guia de Curricularização da Extensão, p. 16)

> Keywords avaliados: `Empreendedorismo, inovadoras, startups, negócios` — 4/4 encontrados

---

#### ✅ EXT-09 — Qual é o objetivo geral da disciplina de extensão?

Com base no Guia de Extensão Curricularizada, o **objetivo geral da disciplina de extensão** é:

**Proporcionar aos estudantes uma compreensão crítica e abrangente da extensão universitária, suas legislações, políticas e função social no contexto da educação superior.**

O foco principal é capacitar os estudantes para:

- Desenvolver projetos que abordem desafios sociais emergentes
- Alinhar suas ações aos Objetivos de Desenvolvimento Sustentável (ODS)
- Atuar de forma consciente e responsável na sociedade
- Aplicar seus conhecimentos acadêmicos na resolução de problemas reais

Ao final da disciplina, você deve ser capaz de:

- Compreender criticamente a extensão universitária, suas legislações e função social
- Integrar o ensino, a pesquisa e a extensão no contexto da educação superior
- Conhecer e aplicar os ODS em seus projetos de extensão
- Projetar e implementar soluções práticas que contribuam para o desenvolvimento de uma sociedade mais justa e consciente

(Fonte: Guia de Curricularização da Extensão, p. 24)

> Keywords avaliados: `objetivo, extensão universitária, ODS, projetos, social` — 5/5 encontrados

---

#### ✅ EXT-10 — O que é o tema norteador da extensão curricularizada?

O **tema norteador da extensão curricularizada** é um tema central definido a cada semestre pelo Núcleo Estruturante da Extensão. Sua função é:

1. **Orientar os projetos** desenvolvidos pelos estudantes, garantindo que estejam alinhados a questões de grande relevância social e interdisciplinar;

2. **Promover uma abordagem integrada** entre teoria e prática, incentivando os estudantes a aplicarem seus conhecimentos acadêmicos em desafios reais da sociedade;

3. **Conectar-se aos Objetivos de Desenvolvimento Sustentável (ODS)** da ONU, voltados para enfrentamento de desafios como erradicação da pobreza, redução das desigualdades, educação de qualidade, inovação tecnológica e sustentabilidade.

Dessa forma, os projetos não apenas fortalecem a formação acadêmica dos estudantes, mas também geram impacto social concreto e promovem transformações significativas na comunidade.

(Fonte: Guia de Curricularização da Extensão, p. 26)

> Keywords avaliados: `tema norteador, semestre, Núcleo Estruturante, ODS` — 4/4 encontrados

---

#### ✅ EXT-11 — O que é o Blackboard e para que serve na disciplina de extensão?

O Blackboard é uma plataforma de aprendizado, mas sua relação específica com a disciplina de extensão no IESB não está coberta pelos guias oficiais que tenho acesso (Guia de Extensão Curricularizada e Guia de Atividades Complementares).

Para informações precisas sobre como o Blackboard é utilizado na disciplina de extensão, recomendo que você:

1. **Entre em contato com a coordenação de extensão** do seu curso;
2. **Envie um e-mail** para **<ativ.complementar@iesb.br>** com sua dúvida;
3. **Consulte o professor** responsável pela disciplina de extensão.

Posso ajudá-lo com dúvidas sobre **regras, prazos, trilhas, avaliação e procedimentos** das atividades complementares e extensão. Há algo específico sobre essas áreas que eu possa esclarecer?

> Keywords avaliados: `Blackboard, plataforma, AVA, IESB` — 4/4 encontrados

---

#### ✅ EXT-12 — O que é a DreamShaper?

Não tenho informações sobre "DreamShaper" nos guias oficiais do IESB sobre Extensão Curricularizada e Atividades Complementares.

A DreamShaper pode ser:

- Uma plataforma ou ferramenta específica que não está documentada nos guias de extensão
- Um projeto, organização ou serviço externo
- Um termo relacionado a um programa específico que não é coberto pela documentação que tenho acesso

**Como posso ajudar?**

Se sua dúvida é sobre como **validar atividades em plataformas externas** como portais ou ambientes de aprendizagem, ou sobre **procedimentos no Aluno Online**, posso ajudar consultando os guias.

Caso precise de informações mais específicas sobre a DreamShaper em relação às atividades complementares do IESB, recomendo contatar:

- **E-mail**: <ativ.complementar@iesb.br>
- **Coordenação de Extensão Curricularizada e Atividades Complementares**

Há algo específico sobre extensão ou atividades complementares que eu possa esclarecer?

> Keywords avaliados: `DreamShaper, plataforma, projeto, interativa` — 3/4 encontrados

---

#### ✅ EXT-13 — Como funciona a avaliação P1 da disciplina de extensão?

A **avaliação P1** da disciplina de extensão funciona da seguinte forma:

## Componentes da P1

1. **Projeto na Plataforma DreamShaper**
   - O projeto será avaliado diretamente na plataforma DreamShaper
   - Todas as etapas devem ser preenchidas na ferramenta
   - Deve atender aos critérios de estrutura, pesquisa, impacto e implementação
   - É importante completar todas as seções para que a avaliação ocorra corretamente

2. **Vídeo Pitch**
   - Apresentação rápida e objetiva do projeto (até 3 minutos)
   - Formato livre: pode incluir falas, slides, animações, entrevistas e outros recursos visuais
   - O vídeo deve deixar claro:
     - Qual é o problema que o projeto pretende resolver
     - Qual é a solução proposta e por que ela é relevante
     - Quem será beneficiado e qual será o impacto esperado

## Critério de Aprovação

A avaliação considera a **clareza da proposta, a objetividade na comunicação e o impacto esperado na comunidade**. Para ser aprovado, você deve atingir, no mínimo, **5 pontos** na nota final da disciplina.

**Se não atingir a média necessária na P1**, você terá a oportunidade de fazer a **PS (Prova Substitutiva)**, que substituirá integralmente a P1 e inclui um relatório analítico adicional.

(Fonte: Guia de Curricularização da Extensão, p. 34, 36)

> Keywords avaliados: `P1, projeto, vídeo pitch, DreamShaper, avaliados` — 4/5 encontrados

---

#### ✅ EXT-14 — O que é o Vídeo Pitch e qual a duração máxima?

## O que é Vídeo Pitch?

O **Vídeo Pitch é uma apresentação rápida e objetiva do seu projeto**, destacando sua proposta, relevância social e impacto esperado.

Ele deve comunicar claramente:

- ✓ Qual é o problema que o projeto pretende resolver?
- ✓ Qual é a solução proposta e por que ela é relevante?
- ✓ Quem será beneficiado e qual será o impacto esperado?

## Duração Máxima

**Até 3 minutos** de duração.

## Formato

O formato é livre, podendo incluir:

- Falas do grupo
- Slides
- Animações
- Entrevistas
- Outros recursos visuais criativos

O vídeo deve estar em **formato horizontal (paisagem)**, com resolução mínima de 1024 x 768 pixels na proporção 16:9.

## Submissão

O vídeo deve ser enviado através do **Blackboard**, anexando o arquivo na atividade intitulada "Vídeo Pitch".

(Fonte: Guia de Curricularização da Extensão, p. 36)

> Keywords avaliados: `Vídeo Pitch, 3 minutos, proposta, relevância social` — 4/4 encontrados

---

#### ✅ EXT-15 — O que é a PS da disciplina de extensão e como ela substitui a P1?

Com base nos guias oficiais, aqui está a explicação sobre PS e como ela substitui a P1:

## O que é PS na disciplina de extensão?

**PS (Prova Substitutiva)** é uma avaliação oferecida aos estudantes que **não atingiram a média necessária na P1**.

## Como a PS substitui a P1?

A PS **substitui integralmente a P1**, sem possibilidade de somatória ou compensação. Ou seja:

- A nota da PS será a única nota considerada (não será somada com a P1)
- Toda a avaliação anterior é desconsiderada

## O que é avaliado na PS?

A PS consiste em três componentes:

1. **Projeto realizado na Plataforma Interativa** - entregue via AVA
2. **Vídeo pitch** - enviado via AVA
3. **Relatório Analítico** - sobre um projeto social existente na cidade do estudante, abordando sua relevância e impacto social

Na P1, o estudante era avaliado apenas pelo projeto e vídeo pitch. Na PS, há um componente adicional (o relatório analítico) que reforça a análise crítica do estudante sobre extensão e impacto social.

Para ser aprovado, é necessário atingir o mínimo de 5 pontos na nota final da disciplina.

(Fonte: Guia de Curricularização da Extensão, p. 34)

> Keywords avaliados: `PS, P1, substitui, relatório analítico, média` — 5/5 encontrados

---

#### ✅ EXT-16 — O que é o relatório analítico e quando devo entregá-lo?

## O que é o Relatório Analítico

O **relatório analítico** é um documento que avalia sua capacidade de pesquisar, analisar e refletir sobre um projeto, preferencialmente em sua cidade ou região, alinhado ao tema norteador do semestre. Caso não seja possível encontrar um projeto local, você pode escolher iniciativas de outras localidades, desde que estejam diretamente relacionadas ao tema.

O relatório deve ser:

- **Técnico, analítico e bem fundamentado**
- Seguindo as normas da **ABNT**
- Com referências bibliográficas e documentais que sustentem a pesquisa

### Estrutura esperada

1. **Introdução** – Apresentação do tema e justificativa da escolha
2. **Histórico da Instituição** – Informações sobre a organização (nome, ano de fundação, missão e valores)
3. **Público-Alvo** – Quem são os beneficiários (faixa etária, perfil socioeconômico, localização)
4. **Demandas Atendidas** (e outras seções conforme solicitado)

---

## Quando Entregar

O **prazo de entrega** varia conforme a modalidade de ensino (presencial ou EaD) e é divulgado no **cronograma semestral/trimestral** disponibilizado no início de cada ciclo acadêmico.

Você encontrará o **calendário acadêmico completo** e os prazos específicos em:

- **Blackboard** – nas turmas da disciplina de extensão
- **Site oficial do IESB** – <http://apps.iesb.br/sistemasAcademicos/calendario>

**⚠️ Atenção Formandos:** Se você é provável formando, deve entregar todas as atividades complementares até o **último dia do período letivo** de integralização do curso.

(Fonte: Guia de Curricularização da Extensão, p. 38, 40-41; Guia de Atividades Complementares Atualizado, p. 13)

> Keywords avaliados: `relatório analítico, projeto, tema norteador, ABNT` — 4/4 encontrados

---

#### ✅ EXT-17 — Sou obrigado a fazer a disciplina de extensão?

Sim, você é **obrigado** a fazer a disciplina de extensão!

Conforme a Resolução nº 7/2018 do MEC, a realização das disciplinas de extensão é **obrigatória para todos os cursos de graduação**. A extensão deve ocupar, no mínimo, **10% da carga horária total do seu curso**.

No IESB, essa exigência é cumprida oferecendo disciplinas de extensão ao longo de todo o curso, com a possibilidade de escolher entre **quatro trilhas de aprendizagem** para que você possa ter uma experiência prática e significativa em sua área de interesse.

Importante: a disciplina de extensão é avaliada como qualquer outra e você pode reprovar nela. Para ser aprovado, é necessário alcançar, no mínimo, **5 pontos na nota final**. Caso seja reprovado, você deverá se matricular novamente no módulo seguinte.

**(Fonte: Guia da Extensão Curricularizada, p. 43)**

> Keywords avaliados: `obrigatória, Resolução, 7/2018, MEC, 10%` — 5/5 encontrados

---

#### ✅ EXT-18 — Como sei em qual trilha fui alocado se não escolhi a tempo?

Ótimo! Encontrei a informação que você precisa.

**Se não escolheu a trilha no prazo:**

Você receberá um **e-mail informando a trilha em que foi alocado(a)**. A alocação é automática e segue a aderência ao seu curso.

**Você pode mudar de trilha:**

Após receber o e-mail com a trilha designada, você terá **até 3 dias corridos** para solicitar uma alteração, caso queira mudar para outra trilha. Fique atento:

- A mudança está sujeita à **disponibilidade de vagas** na trilha desejada
- Após os 3 dias, a alocação se torna **definitiva**

**Como fazer a alteração:**
Acesse o sistema **Aluno Online** e faça a solicitação dentro do prazo de 3 dias.

💡 **Dica:** Acompanhe seu e-mail para receber a notificação de alocação e não perca o prazo de 3 dias para solicitar mudança, se necessário. As datas exatas estão disponíveis no calendário acadêmico.

(Fonte: Guia de Extensão Curricularizada, p. 44)

> Keywords avaliados: `e-mail, alocado, prazo, trilha, automaticamente` — 4/5 encontrados

---

#### ✅ EXT-19 — Posso alterar a minha trilha de extensão depois de alocado?

Sim, você pode alterar sua trilha de extensão após a alocação!

Aqui estão as informações importantes:

**Como funciona:**

- Após ser alocado automaticamente em uma trilha, você receberá um e-mail informando qual foi sua designação
- Você terá **até 3 dias corridos** para solicitar a alteração de trilha
- A mudança está sujeita à **disponibilidade de vagas** na trilha desejada

**Como fazer a alteração:**

1. Acesse o Portal **Aluno Online**
2. Vá para **Serviços Acadêmicos**
3. Selecione **"Requerimento de Trilha de Extensão"**
4. Clique em **"Abrir Solicita Realização"** e escolha a nova trilha desejada

**Importante:**

- O prazo de **3 dias corridos** é contado a partir da sua alocação
- Após esse período, a alocação se torna definitiva
- As datas exatas estão no **calendário acadêmico** do IESB

Fique atento aos prazos! É responsabilidade sua acompanhar as informações do calendário acadêmico e fazer a solicitação dentro do período estipulado.

(Fonte: Guia de Curricularização da Extensão, p. 19 e 44)

> Keywords avaliados: `alterar, trilha, prazo, calendário` — 4/4 encontrados

---

#### ✅ EXT-20 — Como verifico se estou matriculado na disciplina de extensão?

Para verificar se você está matriculado na disciplina de extensão, você deve:

**Acessar o portal Aluno Online** e verificar no menu de **disciplinas matriculadas**. A disciplina de extensão aparecerá listada junto com as demais disciplinas do semestre/trimestre.

(Fonte: Guia de Extensão Curricularizada, p. 44)

> Keywords avaliados: `Aluno Online, matriculado, disciplinas, portal` — 4/4 encontrados

---
