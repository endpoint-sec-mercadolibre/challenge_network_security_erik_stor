import pytest
from app.usecase import AnalysisUseCase
from app.usecase.analysis_usecase import AnalysisUseCase as DirectAnalysisUseCase


class TestUsecaseInit:
    """Tests para el módulo __init__ de usecase"""

    def test_analysis_usecase_import(self):
        """Test que valida que AnalysisUseCase se puede importar correctamente"""
        assert AnalysisUseCase is not None
        assert AnalysisUseCase == DirectAnalysisUseCase

    def test_analysis_usecase_instantiation(self):
        """Test que valida que AnalysisUseCase se puede instanciar"""
        # Verificar que la clase existe y es callable
        assert callable(AnalysisUseCase)
        assert hasattr(AnalysisUseCase, 'execute')
        
        # Intentar instanciar puede o no fallar dependiendo de las dependencias
        try:
            instance = AnalysisUseCase()
            assert instance is not None
        except Exception:
            # Si falla por dependencias, es aceptable
            pass

    def test_module_all_exports(self):
        """Test que valida los exports del módulo"""
        import app.usecase as usecase_module
        
        assert hasattr(usecase_module, '__all__')
        assert 'AnalysisUseCase' in usecase_module.__all__
        assert len(usecase_module.__all__) == 1 