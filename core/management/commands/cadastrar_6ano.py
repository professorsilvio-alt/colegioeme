import os
from django.core.management.base import BaseCommand
from core.models import Aluno, Turma

class Command(BaseCommand):
    help = 'Cadastra alunos do 6o ano que foram extraidos localmente.'

    def handle(self, *args, **options):
        dados = [
            ("61", "Davi Leopoldino Costa", "alunos/fotos/61_davi_leopoldino_costa.jpg"),
            ("61", "Eduardo Afonso Ribeiro", "alunos/fotos/61_eduardo_afonso_ribeiro.jpg"),
            ("61", "Eduardo Gaio Costa", "alunos/fotos/61_eduardo_gaio_costa.jpg"),
            ("61", "Fernanda de Carvalho Dias", "alunos/fotos/61_fernanda_de_carvalho_dias.jpg"),
            ("61", "Gabriel Cocenza Gonçalves", "alunos/fotos/61_gabriel_cocenza_gon_alves.jpg"),
            ("61", "Guilherme Araujo Claudino", "alunos/fotos/61_guilherme_araujo_claudino.jpg"),
            ("61", "Henry da Silva Miranda", "alunos/fotos/61_henry_da_silva_miranda.jpg"),
            ("61", "Isa Ceciliano da Costa Pereira", "alunos/fotos/61_isa_ceciliano_da_costa_pereira.jpg"),
            ("61", "Isabela de Oliveira Collaço Côrtes", "alunos/fotos/61_isabela_de_oliveira_colla_o_c_rtes.jpg"),
            ("61", "Isabella do Espirito Santo Afonso", "alunos/fotos/61_isabella_do_espirito_santo_afonso.jpg"),
            ("61", "Joacy Jacy Cabral Junior", "alunos/fotos/61_joacy_jacy_cabral_junior.jpg"),
            ("61", "João Kalleo Martins Pereira", "alunos/fotos/61_jo_o_kalleo_martins_pereira.jpg"),
            ("61", "Larissa de Almeida Leite", "alunos/fotos/61_larissa_de_almeida_leite.jpg"),
            ("61", "Lucas Azaf  Poiam Romão Haller", "alunos/fotos/61_lucas_azaf__poiam_rom_o_haller.jpg"),
            ("61", "Luiza da Silva Dantas", "alunos/fotos/61_luiza_da_silva_dantas.jpg"),
            ("61", "Marcos Pedro Sarto da Silva Ribeiro", "alunos/fotos/61_marcos_pedro_sarto_da_silva_ribeiro.jpg"),
            ("61", "Maria Clara dos Santos Rafael", "alunos/fotos/61_maria_clara_dos_santos_rafael.jpg"),
            ("61", "Natasha Saba", "alunos/fotos/61_natasha_saba.jpg"),
            ("61", "Ricardo Wang He", "alunos/fotos/61_ricardo_wang_he.jpg"),
            ("61", "Tonny Wu Liang", "alunos/fotos/61_tonny_wu_liang.jpg"),
            ("61", "Valentina Chiabai de Carvalho da Silva", "alunos/fotos/61_valentina_chiabai_de_carvalho_da_silva.jpg"),
            ("62", "Ana Pereira Henriques", "alunos/fotos/62_ana_pereira_henriques.jpg"),
            ("62", "Arthur Gomes França", "alunos/fotos/62_arthur_gomes_fran_a.jpg"),
            ("62", "Bernardo Monteiro de Arruda", "alunos/fotos/62_bernardo_monteiro_de_arruda.jpg"),
            ("62", "Camila Oros Salazar", "alunos/fotos/62_camila_oros_salazar.jpg"),
            ("62", "Davi Gaudard Silva", "alunos/fotos/62_davi_gaudard_silva.jpg"),
            ("62", "Davi dos Santos Azevedo", "alunos/fotos/62_davi_dos_santos_azevedo.jpg"),
            ("62", "Gabriel Calixto de Lira", "alunos/fotos/62_gabriel_calixto_de_lira.jpg"),
            ("62", "Júlia Albuquerque de Aguiar", "alunos/fotos/62_j_lia_albuquerque_de_aguiar.jpg"),
            ("62", "Larah da Silva de Souza", "alunos/fotos/62_larah_da_silva_de_souza.jpg"),
            ("62", "Luiza Almeida das Chagas", "alunos/fotos/62_luiza_almeida_das_chagas.jpg"),
            ("62", "Maitê Souza Chagas", "alunos/fotos/62_mait__souza_chagas.jpg"),
            ("62", "Manuela Figueiredo Guimarães", "alunos/fotos/62_manuela_figueiredo_guimar_es.jpg"),
            ("62", "Maria Carolina Pecorone dos Reis", "alunos/fotos/62_maria_carolina_pecorone_dos_reis.jpg"),
            ("62", "Maria Clara Ribeiro Teixeira", "alunos/fotos/62_maria_clara_ribeiro_teixeira.jpg"),
            ("62", "Maria Luísa Garcia Fernandes", "alunos/fotos/62_maria_lu_sa_garcia_fernandes.jpg"),
            ("62", "Nicolas Santos da Silva", "alunos/fotos/62_nicolas_santos_da_silva.jpg"),
            ("62", "Nicolas Teixeira Andrade da Costa", "alunos/fotos/62_nicolas_teixeira_andrade_da_costa.jpg"),
            ("62", "Rafael Amorim Alves", "alunos/fotos/62_rafael_amorim_alves.jpg"),
            ("62", "Sarah da Silva Almeida", "alunos/fotos/62_sarah_da_silva_almeida.jpg"),
            ("62", "Sofia Costa Mendes Calvalcanti", "alunos/fotos/62_sofia_costa_mendes_calvalcanti.jpg"),
            ("63", "Alice Machado do Nascimento Silva", "alunos/fotos/63_alice_machado_do_nascimento_silva.jpg"),
            ("63", "Arthur de Meneses Bromberg", "alunos/fotos/63_arthur_de_meneses_bromberg.jpg"),
            ("63", "Bernardo Martins de Souza Cunha", "alunos/fotos/63_bernardo_martins_de_souza_cunha.jpg"),
            ("63", "Bernardo de Oliveira Silva Amorim", "alunos/fotos/63_bernardo_de_oliveira_silva_amorim.jpg"),
            ("63", "Betina Cascardo Gonzalez", "alunos/fotos/63_betina_cascardo_gonzalez.jpg"),
            ("63", "Daniel Eccard Hennig Dill", "alunos/fotos/63_daniel_eccard_hennig_dill.jpg"),
            ("63", "Eduarda Rodrigues Sant' Anna", "alunos/fotos/63_eduarda_rodrigues_sant__anna.jpg"),
            ("63", "Giovanna Alves Rodrigues", "alunos/fotos/63_giovanna_alves_rodrigues.jpg"),
            ("63", "Isabely Vitor Chagas Pinho", "alunos/fotos/63_isabely_vitor_chagas_pinho.jpg"),
            ("63", "João Gabriel Santos Cunha", "alunos/fotos/63_jo_o_gabriel_santos_cunha.jpg"),
            ("63", "João Pedro Gonçalves da Silva Souza", "alunos/fotos/63_jo_o_pedro_gon_alves_da_silva_souza.jpg"),
            ("63", "Juliana Barroso Pereira", "alunos/fotos/63_juliana_barroso_pereira.jpg"),
            ("63", "Lara Carla dos Santos Almeida", "alunos/fotos/63_lara_carla_dos_santos_almeida.jpg"),
            ("63", "Luíza Hipólito da Silva Rosa", "alunos/fotos/63_lu_za_hip_lito_da_silva_rosa.jpg"),
            ("63", "Manuela Fernandes Ribeiro Sanches", "alunos/fotos/63_manuela_fernandes_ribeiro_sanches.jpg"),
            ("63", "Maria Eduarda Binttancurt Machado", "alunos/fotos/63_maria_eduarda_binttancurt_machado.jpg"),
            ("63", "Maria Eduarda Oliveira Dantas", "alunos/fotos/63_maria_eduarda_oliveira_dantas.jpg"),
            ("63", "Maria Luísa Nogueira de Andrade", "alunos/fotos/63_maria_lu_sa_nogueira_de_andrade.jpg"),
            ("63", "Mariana Bento da Silva Rangel", "alunos/fotos/63_mariana_bento_da_silva_rangel.jpg"),
            ("63", "Rafael Pontes de Oliveira Lopes", "alunos/fotos/63_rafael_pontes_de_oliveira_lopes.jpg"),
            ("63", "Rebeca Vitória Coutinho Alves da Rocha", "alunos/fotos/63_rebeca_vit_ria_coutinho_alves_da_rocha.jpg"),
            ("63", "Sarah Helena dos Santos Berlitz", "alunos/fotos/63_sarah_helena_dos_santos_berlitz.jpg"),
            ("63", "Sophia Sodré Grande", "alunos/fotos/63_sophia_sodr__grande.jpg"),
        ]
        criados = 0
        for cod_turma, nome, foto_name in dados:
            try:
                turma = Turma.objects.get(codigo=cod_turma)
                aluno, created = Aluno.objects.get_or_create(turma=turma, nome=nome)
                if foto_name:
                    aluno.foto.name = foto_name
                    aluno.save(update_fields=['foto'])
                if created:
                    criados += 1
            except Turma.DoesNotExist:
                self.stdout.write(f'Turma {cod_turma} nao encontrada.')
        
        self.stdout.write(self.style.SUCCESS(f'Concluido! {criados} alunos do 6o ano criados/atualizados.'))
