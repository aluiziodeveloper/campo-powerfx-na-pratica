*Material de apoio do Capítulo 24, transcrito do livro. Use por recorte, como o capítulo explica: inteira uma vez, só os degraus tocados a cada publicação, inteira de novo a cada semestre. O que não for marcado vai para o Registro de Decisões, com o risco e o nome de quem o aceitou.*

# Checklist de Produção — 40 itens

Organizada pelos **dez degraus** da escada *Funciona ≠ Está pronto*, com o capítulo de origem ao lado de cada item. Quatro itens por degrau, em média.

**Como usar:** como **lista de consciência**, e não de aprovação. Item não cumprido não impede a publicação — impede a publicação **silenciosa**. O que não foi feito é declarado no *Registro de Decisões*, com o risco e a data de revisão.

Uma checklist que reprova sempre é abandonada na terceira semana. Esta não reprova: ela ilumina.

### Funciona
- [ ] O caminho principal foi percorrido por outra pessoa, num aparelho que não é o seu | Cap. 4
- [ ] Todas as telas abrem sem erro, incluindo as que você não mexeu | Cap. 24
- [ ] Um registro foi criado, editado e excluído com sucesso | Cap. 13
- [ ] O tempo de abertura foi medido no aparelho do usuário, e o limite aceitável foi combinado com quem usa | Cap. 16

### Correta
- [ ] Todo campo que pode vir em branco tem tratamento decidido e escrito | Cap. 6
- [ ] A consulta principal delega na fonte atual, verificado na tabela com data | Caps. 10, 11
- [ ] Os três cenários de conflito de escrita foram exercitados | Cap. 14
- [ ] O roteiro de regressão foi executado sem falha | Cap. 24

### Legível
- [ ] Nenhuma fórmula precisa ser copiada para fora para ser lida | Cap. 5
- [ ] Toda fórmula com mais de três operações tem comentário de intenção | Cap. 5
- [ ] Controles seguem a convenção de nomes da aplicação | Cap. 4
- [ ] Funções próprias têm tipo de entrada e saída declarados | Cap. 17

### Reutilizável
- [ ] Nenhuma regra de negócio aparece em mais de um lugar | Cap. 17
- [ ] A biblioteca de componentes está versionada e documentada | Cap. 17
- [ ] Constantes e limites estão em `App.Formulas` ou variável de ambiente | Caps. 12, 23
- [ ] Há inventário de funções, com o que cada uma faz | Cap. 17

### Performática
- [ ] Existe ficha de medição do percurso principal, no aparelho e na rede do usuário | Cap. 16
- [ ] O recorte vem antes da moldagem em toda consulta à fonte | Cap. 10
- [ ] Nenhuma consulta não delegável roda sobre volume acima de 500 registros sem justificativa | Cap. 8
- [ ] Dados de referência estão em fórmulas nomeadas no `App.Formulas`, e o `App.OnStart` está vazio | Caps. 2, 12

### Segura
- [ ] Um usuário sem privilégio tentou acessar o que não deve, e não conseguiu | Cap. 21
- [ ] A verificação foi feita com segunda conta, e não com a conta do criador | Cap. 21
- [ ] Nenhum segredo está no código-fonte do aplicativo | Cap. 21
- [ ] Dado pessoal foi identificado e o tratamento está documentado | Cap. 21

### Testável
- [ ] Existe roteiro de regressão escrito, com um caso para cada defeito já corrigido | Cap. 24
- [ ] As funções próprias foram exercitadas com entradas-limite | Cap. 24
- [ ] Existe massa de teste que não é cópia de produção | Cap. 24
- [ ] A revisão de fórmulas foi aplicada com a checklist, e o resultado registrado | Cap. 24

### Governável
- [ ] Existe procedimento de promoção escrito e caminho de volta decidido | Cap. 23
- [ ] A aplicação está empacotada numa solução, com inventário de dependências | Cap. 23
- [ ] Valores que mudam por ambiente estão em variáveis de ambiente | Cap. 23
- [ ] O caminho de volta foi exercitado ao menos uma vez em homologação | Cap. 23

### Operável
- [ ] Há como saber que a aplicação falhou sem depender de um usuário avisar | Cap. 25
- [ ] Existe roteiro de investigação para os cenários de falha previsíveis | Cap. 25
- [ ] O `Trace` está instrumentado nos caminhos críticos | Cap. 25
- [ ] Existe plano de retorno para incidente, com tempo máximo de tentativa | Cap. 25

### Corporativa
- [ ] Existe dono declarado e um substituto que já publicou uma vez | Cap. 25
- [ ] A documentação viva está reunida e atualizada | Cap. 23
- [ ] A transferência de propriedade foi exercitada | Cap. 27
- [ ] O aplicativo sobrevive à saída de quem o construiu | Cap. 27

---

Data: ___/___/______ · Aplicação e versão: ______________ · Quem aplicou: ______________
