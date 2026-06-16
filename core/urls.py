from django.urls import path
from . import views

urlpatterns = [
    path('trocar-senha/', views.forcar_troca_senha, name='forcar_troca_senha'),
    path('cadastrar-email/', views.cadastrar_email, name='cadastrar_email'),
    path('recuperar-senha/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('recuperar-senha/enviado/', views.CustomPasswordResetDoneView.as_view(), name='recuperar_senha_enviada'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # API
    path('api/alunos/<str:codigo>/', views.api_alunos_turma, name='api_alunos_turma'),
    path('api/professores/<int:disc_id>/', views.api_professores_disciplina, name='api_professores_disciplina'),
    path('api/turma/<str:codigo>/disciplinas/', views.api_disciplinas_turma, name='api_disciplinas_turma'),
    path('api/turma/<str:codigo>/disciplina/<int:disc_id>/professores/', views.api_professores_turma_disc, name='api_professores_turma_disc'),
    path('api/turma/<str:codigo>/professor/<int:prof_id>/datas/', views.api_datas_validas, name='api_datas_validas'),
    path('api/professor/<int:prof_id>/grades/', views.api_professor_grades, name='api_professor_grades'),
    path('api/sugestoes/', views.api_sugestoes_conteudo, name='api_sugestoes_conteudo'),
    path('api/conteudo/verificar-duplicidade/', views.api_verificar_duplicidade, name='api_verificar_duplicidade'),
    path('api/conteudo/precheck-coletivo/', views.api_precheck_coletivo, name='api_precheck_coletivo'),

    # Ocorrências
    path('ocorrencia/criar/', views.ocorrencia_criar, name='ocorrencia_criar'),
    path('ocorrencia/<int:pk>/', views.ocorrencia_ver, name='ocorrencia_ver'),
    path('ocorrencia/<int:pk>/editar/', views.ocorrencia_editar, name='ocorrencia_editar'),
    path('ocorrencia/<int:pk>/excluir/', views.ocorrencia_excluir, name='ocorrencia_excluir'),
    path('ocorrencia/excluir-varios/', views.ocorrencia_excluir_varios, name='ocorrencia_excluir_varios'),
    path('ocorrencia/mudar-status/', views.ocorrencia_mudar_status, name='ocorrencia_mudar_status'),
    path('ocorrencia/<int:pk>/status/', views.ocorrencia_mudar_status_direto, name='ocorrencia_mudar_status_direto'),

    # Conteúdos
    path('conteudo/criar/', views.conteudo_criar, name='conteudo_criar'),
    path('conteudo/<int:pk>/', views.conteudo_ver, name='conteudo_ver'),
    path('conteudo/<int:pk>/editar/', views.conteudo_editar, name='conteudo_editar'),
    path('conteudo/<int:pk>/excluir/', views.conteudo_excluir, name='conteudo_excluir'),
    path('conteudo/excluir-varios/', views.conteudo_excluir_varios, name='conteudo_excluir_varios'),
    path('conteudo/confirmar/', views.conteudo_confirmar, name='conteudo_confirmar'),
    path('conteudo/<int:pk>/desconfirmar/', views.conteudo_desconfirmar, name='conteudo_desconfirmar'),
    path('conteudo/desconfirmar-varios/', views.conteudo_desconfirmar_varios, name='conteudo_desconfirmar_varios'),
    path('lancamentos/coletivos/', views.lancamentos_coletivos, name='lancamentos_coletivos'),

    # Exportar
    path('exportar/ocorrencias/csv/', views.exportar_ocorrencias_csv, name='exportar_ocorrencias_csv'),
    path('exportar/ocorrencias/pdf/', views.exportar_ocorrencias_pdf, name='exportar_ocorrencias_pdf'),
    path('exportar/conteudos/csv/', views.exportar_conteudos_csv, name='exportar_conteudos_csv'),
    path('exportar/conteudos/pdf/', views.exportar_conteudos_pdf, name='exportar_conteudos_pdf'),

    # Relatórios Customizados
    path('relatorio-alocacao/', views.relatorio_alocacao, name='relatorio_alocacao'),
    path('exportar/alocacao/pdf/', views.exportar_alocacao_pdf, name='exportar_alocacao_pdf'),

    # Relatórios de Lançamentos Faltantes
    path('relatorios/pendencias/', views.relatorio_pendencias, name='relatorio_pendencias'),
    path('relatorios/pendencias/pdf/', views.exportar_pendencias_pdf, name='relatorio_pendencias_pdf'),
    path('relatorios/pendencias/professor/<int:prof_id>/', views.detalhe_pendencias_professor, name='detalhe_pendencias_professor'),
    path('relatorios/lancamento-coletivo/', views.lancamento_coletivo, name='lancamento_coletivo'),
    path('sugestao/criar-massa/', views.sugestao_criar_massa, name='sugestao_criar_massa'),
    path('aulas-extras/upload/', views.upload_aulas_extras, name='upload_aulas_extras'),
    path('gerenciar-sugestoes/', views.gerenciar_sugestoes, name='gerenciar_sugestoes'),
    path('sugestao/<int:pk>/editar/', views.sugestao_editar, name='sugestao_editar'),
    path('sugestao/<int:pk>/excluir/', views.sugestao_excluir, name='sugestao_excluir'),
    path('sugestoes/acoes-massa/', views.sugestoes_acoes_massa, name='sugestoes_acoes_massa'),
    path('migrar-alunos/', views.migrar_alunos, name='migrar_alunos'),
    path('escola/configurar/', views.escola_configurar, name='escola_configurar'),
    path('escola/professores/', views.escola_professores_list, name='escola_professores_list'),
    path('escola/professores/novo/', views.escola_professor_novo, name='escola_professor_novo'),
    path('escola/professores/<int:pk>/editar/', views.escola_professor_edit, name='escola_professor_edit'),

    # Notas
    path('notas/', views.notas_index, name='notas_index'),
    path('notas/turma/<str:codigo>/<int:bimestre>/', views.notas_turma, name='notas_turma'),
    path('notas/salvar/', views.nota_salvar, name='nota_salvar'),
    path('notas/aplicar-na/', views.aplicar_na_bimestre, name='aplicar_na_bimestre'),
    path('notas/remover-na/', views.remover_na, name='remover_na'),
    path('notas/aluno/<int:pk>/', views.boletim_aluno, name='boletim_aluno'),
    path('notas/boletim/<str:codigo>/', views.boletim_turma, name='boletim_turma'),

    # Secretaria — Períodos de lançamento
    path('secretaria/periodos-notas/', views.config_periodos_notas, name='config_periodos_notas'),
]
