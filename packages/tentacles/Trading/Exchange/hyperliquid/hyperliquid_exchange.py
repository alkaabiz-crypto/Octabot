#  Drakkar-Software OctoBot-Tentacles
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import typing

import octobot_trading.enums as trading_enums
import octobot_trading.exchanges as exchanges
import octobot_trading.exchanges.connectors.ccxt.constants as ccxt_constants

_FETCH_MARKETS_TYPES = "types"
_SPOT_MARKET_TYPES = ["spot"]
# "swap" are native perpetuals, "hip3" are builder-deployed perpetuals (ex: XYZ-CL/USDC:USDC for WTI oil)
_FUTURE_MARKET_TYPES = ["swap", "hip3"]
_MARKET_INFO = "info"
_DEX_PARAM = "dex"


class HyperliquidConnector(exchanges.CCXTConnector):

    def _client_factory(
        self,
        force_unauth,
        keys_adapter: typing.Callable[[exchanges.ExchangeCredentialsData], exchanges.ExchangeCredentialsData]=None
    ) -> tuple:
        return super()._client_factory(force_unauth, keys_adapter=self._keys_adapter)

    def _keys_adapter(self, creds: exchanges.ExchangeCredentialsData) -> exchanges.ExchangeCredentialsData:
        # use api key and secret as wallet address and private key
        creds.wallet_address = creds.api_key
        creds.private_key = creds.secret
        creds.api_key = creds.secret = None
        return creds

    async def get_funding_rate(self, symbol: str, **kwargs: dict) -> dict:
        return await super().get_funding_rate(symbol, **self._with_hip3_dex_param(symbol, kwargs))

    def _with_hip3_dex_param(self, symbol: str, params: dict) -> dict:
        # HIP-3 perpetuals live on their own dex (ex: "xyz" for XYZ-CL/USDC:USDC): without it,
        # hyperliquid only returns native perpetuals data and HIP-3 funding rates are missing
        dex = (self.client.markets or {}).get(symbol, {}).get(_MARKET_INFO, {}).get(_DEX_PARAM)
        if dex and _DEX_PARAM not in params:
            return {**params, _DEX_PARAM: dex}
        return params


class Hyperliquid(exchanges.RestExchange):
    DEFAULT_CONNECTOR_CLASS = HyperliquidConnector

    @classmethod
    def get_name(cls):
        return 'hyperliquid'

    @classmethod
    def get_supported_exchange_types(cls) -> list:
        """
        :return: The list of supported exchange types
        """
        return [
            trading_enums.ExchangeTypes.SPOT,
            # perpetuals, including HIP-3 builder markets such as XYZ-CL/USDC:USDC (WTI oil)
            trading_enums.ExchangeTypes.FUTURE,
        ]

    def get_additional_connector_config(self):
        # the bundled ob_hyperliquid client only loads spot markets by default:
        # load perpetuals (native and HIP-3 builder dexes) when trading futures
        return {
            ccxt_constants.CCXT_OPTIONS: {
                ccxt_constants.CCXT_FETCH_MARKETS: {
                    _FETCH_MARKETS_TYPES: (
                        _FUTURE_MARKET_TYPES if self.exchange_manager.is_future else _SPOT_MARKET_TYPES
                    ),
                },
            },
        }
