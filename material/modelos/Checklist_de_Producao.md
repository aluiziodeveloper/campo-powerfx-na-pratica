*Material de apoio do Capítulo 25, transcrito do livro. Use por recorte, como o capítulo explica: inteira uma vez, só os degraus tocados a cada publicação, inteira de novo a cada semestre. O que não for marcado vai para o Registro de Decisões, com o risco e o nome de quem o aceitou.*

# Checklist de Produção — 40 itens

Organizada pelos **dez degraus** da escada *Funciona ≠ Está pronto*, com o capítulo de origem ao lado de cada item. Quatro itens por degrau, em média.

**Como usar:** como **lista de consciência**, e não de aprovação. Item não cumprido não impede a publicação — impede a publicação **silenciosa**. O que não foi feito é declarado no *Registro de Decisões*, com o risco e a data de revisão.

Uma checklist que reprova sempre é abandonada na terceira semana. Esta não reprova: ela ilumina.

### Funciona
- [ ] O caminho principal foi percorrido por outra pessoa, num aparelho que não é o seu | Cap. 5
- [ ] Todas as telas abrem sem erro, incluindo as que você não mexeu | Cap. 25
- [ ] Um registro foi criado, editado e excluído com sucesso | Cap. 14
- [ ] O tempo de abertura foi medido no aparelho do usuário, e o limite aceitável foi combinado com quem usa | Cap. 17

### Correta
- [ ] Todo campo que pode vir em branco tem tratamento decidido e escrito | Cap. 7
- [ ] A consulta principal delega na fonte atual, verificado na tabela com data | Caps. 11, 12
- [ ] Os três cenários de conflito de escrita foram exercitados | Cap. 15
- [ ] O roteiro de regressão foi executado sem falha | Cap. 25

### Legível
- [ ] Nenhuma fórmula precisa ser copiada para fora para ser lida | Cap. 6
- [ ] Toda fórmula com mais de três operações tem comentário de intenção | Cap. 6
- [ ] Controles seguem a convenção de nomes da aplicação | Cap. 5
- [ ] Funções próprias têm tipo de entrada e saída declarados | Cap. 18

### Reutilizável
- [ ] Nenhuma regra de negócio aparece em mais de um lugar | Cap. 18
- [ ] A biblioteca de componentes está versionada e documentada | Cap. 18
- [ ] Constantes e limites estão em `App.Formulas` ou variável de ambiente | Caps. 13, 24
- [ ] Há inventário de funções, com o que cada uma faz | Cap. 18

### Performática
- [ ] Existe ficha de medição do percurso principal, no aparelho e na rede do usuário | Cap. 17
- [ ] O recorte vem antes da moldagem em toda consulta à fonte | Cap. 11
- [ ] Nenhuma consulta não delegável roda sobre volume acima de 500 registros sem justificativa | Cap. 9
- [ ] Dados de referência estão em fórmulas nomeadas no `App.Formulas`, e o `App.OnStart` está vazio | Caps. 3, 13

### Segura
- [ ] Um usuário sem privilégio tentou acessar o que não deve, e não conseguiu | Cap. 22
- [ ] A verificação foi feita com segunda conta, e não com a conta do criador | Cap. 22
- [ ] Nenhum segredo está no código-fonte do aplicativo | Cap. 22
- [ ] Dado pessoal foi identificado e o tratamento está documentado | Cap. 22

### Testável
- [ ] Existe roteiro de regressão escrito, com um caso para cada defeito já corrigido | Cap. 25
- [ ] As funções próprias foram exercitadas com entradas-limite | Cap. 25
- [ ] Existe massa de teste que não é cópia de produção | Cap. 25
- [ ] A revisão de fórmulas foi aplicada com a checklist, e o resultado registrado | Cap. 25

### Governável
- [ ] Existe procedimento de promoção escrito e caminho de volta decidido | Cap. 24
- [ ] A aplicação está empacotada numa solução, com inventário de dependências | Cap. 24
- [ ] Valores que mudam por ambiente estão em variáveis de ambiente | Cap. 24
- [ ] O caminho de volta foi exercitado ao menos uma vez em homologação | Cap. 24

### Operável
- [ ] Há como saber que a aplicação falhou sem depender de um usuário avisar | Cap. 26
- [ ] Existe roteiro de investigação para os cenários de falha previsíveis | Cap. 26
- [ ] O `Trace` está instrumentado nos caminhos críticos | Cap. 26
- [ ] Existe plano de retorno para incidente, com tempo máximo de tentativa | Cap. 26

### Corporativa
- [ ] Existe dono declarado e um substituto que já publicou uma vez | Cap. 26
- [ ] A documentação viva está reunida e atualizada | Cap. 24
- [ ] A transferência de propriedade foi exercitada | Cap. 28
- [ ] O aplicativo sobrevive à saída de quem o construiu | Cap. 28

---

Data: ___/___/______ · Aplicação e versão: ______________ · Quem aplicou: ______________
