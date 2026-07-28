from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.domain.collections.gbank_account import GBankAccount
from src.domain.collections.gconsignee import GConsignee
from src.domain.collections.gcountry import Gcountry
from src.domain.collections.gexporter import GExporter
from src.domain.collections.ginvitation import GInvitation
from src.domain.collections.gmanufacturer import GManufacturer
from src.domain.collections.gpassword_reset import GPasswordReset
from src.domain.collections.gsupplier import GSupplier
from src.infrastructure.persistence.documents.colour_document import ColourDocument
from src.infrastructure.persistence.documents.consignee_document import ConsigneeDocument
from src.domain.dtos.paged_result_dto import PagedResult
from src.domain.dtos.register_dto import RegisterUserDto
from src.domain.dtos.login_dto import LoginDto
from src.infrastructure.persistence.documents.order_document import OrderDocument

class IMongoRepo(ABC):
    
    @abstractmethod
    async def save_colour_async(self, Colour: ColourDocument) -> ColourDocument:
        """Contrato para guardar o buscar un Colour por nombre"""
        pass

    @abstractmethod
    async def get_colour_list_async(self) -> List[ColourDocument]:
        """Contrato para obtener la lista de Coloures ordenados por nombre"""
        pass

    @abstractmethod
    async def delete_colour_async(self, Colour_id: str) -> Optional[ColourDocument]:
        """Contrato para eliminar un Colour por su ID"""
        pass

    @abstractmethod
    async def save_consignee_async(self, consignee: ConsigneeDocument) -> ConsigneeDocument:
        """Contrato para registrar un consignee"""
        pass

    @abstractmethod
    async def update_consignee_async(self, consignee_id: str, consignee: ConsigneeDocument) -> Optional[ConsigneeDocument]:
        """Contrato para actualizar un consignee"""
        pass

    @abstractmethod
    async def delete_consignee_async(self, consignee_id: str) -> Optional[ConsigneeDocument]:
        """Contrato para eliminar un consignee"""
        pass

    @abstractmethod
    async def consignee_list_async(self, page_number: int = 1, page_size: int = 10) -> PagedResult[ConsigneeDocument]:
        """Contrato para listar consignees paginados"""
        pass

    @abstractmethod
    async def get_list_consignee_async(self) -> Optional[List[ConsigneeDocument]]:
        """Contrato para obtener lista completa de consignees si hay más de uno"""
        pass

    @abstractmethod
    async def get_country_list_async(self) -> List[Gcountry]:
        """Contrato para obtener la lista de países"""
        pass
    
    @abstractmethod
    async def register_user_async(self, dto: RegisterUserDto) -> Dict[str, Any]:
        """Contrato para el registro de un usuario"""
        pass

    @abstractmethod
    async def login_user_async(self, dto: LoginDto) -> Dict[str, Any]:
        """Contrato para el login de un usuario"""
        pass

    @abstractmethod
    async def get_proforma_number(self) -> int:
        """Contrato para obtener el numero de la proforma"""
        pass

    @abstractmethod
    async def save_order(self, order: OrderDocument) -> OrderDocument:
        """Contrato para guardar la orden"""
        pass

    @abstractmethod
    async def update_pi_number(self, pi: int) -> int:
        """Contrato para actualizar el numero de la proforma"""
        pass

    @abstractmethod
    async def get_consignee_by_id(self, consignee_id: str) -> Optional[GConsignee]:
        """Contrato para obtener consignee por id"""
        pass

    @abstractmethod
    async def get_supplier_by_id(self, supplier_id: str) -> Optional[GSupplier]:
        """Contrato para obtener supplier por id"""
        pass

    @abstractmethod
    async def get_exporter_by_id(self, exporter_id: str) -> Optional[GExporter]:
        """Contrato para obtener exporter por id"""
        pass
    
    @abstractmethod
    async def get_manufacturer_by_id(self, manufacturer_id: str) -> Optional[GManufacturer]:
        """Contrato para obtener manufacturer por id"""
        pass

    @abstractmethod
    async def get_bank_account_by_id(self, bank_account_id: str) -> Optional[GBankAccount]:
        """Contrato para obtener bank account por id"""
        pass

    @abstractmethod
    async def create_invitation_async(self, invitation: GInvitation) -> GInvitation:
        """Contrato para registrar una nueva invitación generada por el admin"""
        pass

    @abstractmethod
    async def verify_and_use_invitation_async(self, code_str: str) -> Dict[str, Any]:
        """Contrato para validar y consumir un código de invitación de un solo uso"""
        pass

    @abstractmethod
    async def create_password_reset_code_async(self, reset_obj: GPasswordReset) -> GPasswordReset:
        """Registra un nuevo código verificador de contraseña"""
        pass

    @abstractmethod
    async def verify_and_use_reset_code_async(self, email: str, code_str: str) -> Dict[str, Any]:
        """Valida y quema el código verificador de contraseña en una sola operación"""
        pass

    @abstractmethod
    async def update_user_password_by_email_async(self, email: str, new_hashed_password: str) -> bool:
        """Actualiza la contraseña de un usuario usando su email"""
        pass

