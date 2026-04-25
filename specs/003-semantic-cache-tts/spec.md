# Feature Specification: Cache Semantico e Resposta em Audio

**Feature Branch**: `[003-before-specify]`  
**Created**: 2026-04-25  
**Status**: Draft  
**Input**: User description: "leia a atividade edi-26 do linear e escreva a especificacao"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reutilizar resposta semantica (Priority: P1)

Como usuario do chat, quero que perguntas com o mesmo sentido reutilizem respostas ja existentes para receber retorno rapidamente e reduzir custo de processamento.

**Why this priority**: Este fluxo gera o maior ganho imediato de eficiencia operacional e reduz chamadas desnecessarias de processamento inteligente.

**Independent Test**: Pode ser testado enviando duas perguntas com significado equivalente; a segunda deve retornar resposta existente sem novo processamento completo.

**Acceptance Scenarios**:

1. **Given** que ja existe uma pergunta equivalente registrada com resposta valida, **When** o usuario envia uma nova pergunta de mesmo sentido, **Then** o sistema retorna a resposta reutilizada sem gerar nova resposta completa.
2. **Given** que nao existe pergunta equivalente registrada, **When** o usuario envia uma pergunta nova, **Then** o sistema gera resposta, registra o par pergunta-resposta e disponibiliza para reutilizacao futura.

---

### User Story 2 - Receber resposta em texto e audio (Priority: P2)

Como usuario do chat, quero receber a resposta em texto e em audio para escolher a forma de consumo mais conveniente.

**Why this priority**: Aumenta acessibilidade e flexibilidade de uso sem alterar o objetivo principal da conversa.

**Independent Test**: Pode ser testado enviando uma pergunta valida e verificando que o retorno contem texto legivel e audio reproduzivel no mesmo payload.

**Acceptance Scenarios**:

1. **Given** que o sistema finalizou o processamento da pergunta, **When** a resposta e retornada ao cliente, **Then** o payload contem o texto da resposta e uma representacao de audio acessivel.
2. **Given** que existe audio previamente gerado para a resposta reutilizada, **When** ocorre reaproveitamento de resposta, **Then** o mesmo audio e retornado sem nova geracao.

---

### User Story 3 - Processar entrada por voz (Priority: P3)

Como usuario que envia audio, quero que minha mensagem seja compreendida e respondida no mesmo fluxo para nao precisar redigitar minha duvida.

**Why this priority**: Complementa a experiencia multimodal e amplia os canais de entrada do usuario.

**Independent Test**: Pode ser testado enviando uma entrada em audio e validando que a transcricao e utilizada para gerar ou reutilizar resposta com retorno em texto e audio.

**Acceptance Scenarios**:

1. **Given** que o usuario envia uma mensagem em audio valida, **When** o sistema recebe a requisicao, **Then** a entrada e transcrita e tratada como pergunta para busca semantica e resposta.
2. **Given** que a transcricao nao pode ser concluida com confianca minima, **When** o sistema processa o audio, **Then** retorna mensagem clara solicitando novo envio sem quebrar o contrato de resposta.

### Edge Cases

- O que acontece quando a similaridade fica muito proxima do limiar de reutilizacao e pode gerar ambiguidades?
- Como o sistema responde quando existe cache semantico com texto, mas o audio associado nao esta disponivel?
- Como o sistema se comporta quando a geracao de audio falha apos o texto da resposta ja ter sido produzido?
- Como tratar entradas vazias, muito longas ou com qualidade de audio insuficiente?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST analisar semanticamente cada pergunta recebida antes de decidir por reutilizacao ou nova geracao de resposta.
- **FR-002**: O sistema MUST identificar perguntas equivalentes por similaridade semantica utilizando um limiar configuravel de correspondencia.
- **FR-003**: O sistema MUST reutilizar texto e audio previamente armazenados quando houver correspondencia semantica acima do limiar definido.
- **FR-004**: O sistema MUST gerar nova resposta quando nao houver correspondencia semantica valida.
- **FR-005**: O sistema MUST armazenar novas perguntas, respostas textuais e referencia de audio para futuras reutilizacoes.
- **FR-006**: O sistema MUST aceitar entrada textual e entrada em audio no mesmo fluxo funcional de atendimento.
- **FR-007**: O sistema MUST transcrever entradas em audio para texto antes da etapa de comparacao semantica.
- **FR-008**: O sistema MUST retornar payload estruturado contendo, no minimo, a resposta textual e a resposta em audio acessivel.
- **FR-009**: O sistema MUST incluir no retorno a transcricao da entrada quando a mensagem original for audio.
- **FR-010**: O sistema MUST registrar eventos operacionais que permitam distinguir reutilizacao de resposta e nova geracao.
- **FR-011**: O sistema MUST tratar falhas de transcricao, busca semantica ou geracao de audio com mensagens de erro claras e sem expor informacoes sensiveis.
- **FR-012**: O sistema MUST garantir consistencia do contrato de resposta para chamadas com cache hit e cache miss.

### Key Entities *(include if feature involves data)*

- **SolicitacaoChat**: Representa a mensagem recebida do usuario, com tipo de entrada (texto ou audio), conteudo original, transcricao (quando aplicavel) e metadados de processamento.
- **RegistroSemantico**: Representa o item reutilizavel para comparacao semantica, incluindo representacao vetorial da pergunta, texto da resposta e dados de correspondencia.
- **RespostaMultimodal**: Representa a resposta final entregue ao cliente, contendo texto, audio acessivel e indicador de origem (reutilizada ou nova).
- **EventoProcessamento**: Representa rastros operacionais da execucao (reuso, nova geracao, falhas controladas) para auditoria funcional e monitoramento.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em ate 30 dias de operacao, pelo menos 60% das perguntas semanticamente equivalentes sao atendidas por reutilizacao de resposta existente.
- **SC-002**: Em pelo menos 95% das requisicoes bem-sucedidas, o usuario recebe texto e audio no mesmo retorno funcional.
- **SC-003**: Pelo menos 90% das entradas em audio validas resultam em transcricao utilizavel sem necessidade de reenvio.
- **SC-004**: O tempo de resposta percebido para perguntas reutilizadas e, no minimo, 40% menor que o de perguntas sem reutilizacao.
- **SC-005**: O percentual de respostas bem-sucedidas com contrato completo (texto + audio + campos obrigatorios) permanece acima de 99% apos a implantacao.

## Assumptions

- O recurso sera aplicado ao mesmo publico e canal de atendimento ja cobertos pelas features anteriores do motor de chat.
- O limiar de equivalencia semantica sera parametrizavel por configuracao de produto sem exigir alteracao de fluxo do usuario.
- A disponibilizacao de audio podera ocorrer como conteudo embutido ou referencia temporaria, desde que o cliente consiga reproduzir o retorno sem etapa manual adicional.
- O fluxo de seguranca e validacao de entrada ja existente permanece obrigatorio e antecede o processamento semantico.
- O escopo desta entrega cobre processamento de uma solicitacao por vez e nao inclui funcionalidades de edicao manual de cache por usuario final.
