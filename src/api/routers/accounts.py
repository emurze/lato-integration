from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from api.deps import get_application
from api.schemas.accounts import AccountJsonResponse, AccountJsonRequest
from modules.accounts.application.command import CreateAccountCommand
from modules.accounts.application.query import GetAccountQuery
from seedwork.application.application import Application
from seedwork.domain.errors import ErrorType
from seedwork.presentation.error_handling import handle_errors
from seedwork.presentation.schemas import FailedJsonResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get(
    "/{account_id}",
    response_model=AccountJsonResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": FailedJsonResponse},
    },
)
async def get_account(
    account_id: UUID,
    app: Application = Depends(get_application),
):
    res = await app.execute_async(GetAccountQuery(id=account_id))
    handle_errors(res, [ErrorType.NOT_FOUND])
    return res.payload


@router.post(
    "/",
    response_model=AccountJsonResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_account(
    request_body: AccountJsonRequest,
    app: Application = Depends(get_application),
):
    command = CreateAccountCommand.model_validate(request_body)
    await app.execute_async(command)
    res = await app.execute_async(GetAccountQuery(id=command.id))
    return res.payload
