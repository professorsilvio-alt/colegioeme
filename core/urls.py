from django.urls import path
from . import views

urlpatterns = [
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
    path('gerenciar-sugestoes/', views.gerenciar_sugestoes, name='gerenciar_sugestoes'),
]
