"""帳戶管理模組

此模組負責處理永豐 Shioaji API 的帳戶餘額、持倉與損益功能。
"""

import shioaji as sj
from typing import List, Optional, Any, Dict
from datetime import datetime


class AccountManager:
    """負責獲取帳戶餘額與損益資訊
    
    此類別封裝了永豐 Shioaji API 的帳戶管理功能，
    提供帳戶餘額、持倉、已實現與未實現損益的查詢。
    """
    
    def __init__(self, api: sj.Shioaji) -> None:
        """初始化帳戶管理器
        
        Args:
            api (sj.Shioaji): 已登入的 Shioaji API 物件
        
        Raises:
            ValueError: 當傳入的 API 物件為 None 時
        """
        if api is None:
            raise ValueError("API 物件不可為 None")
        
        self._api = api
        self._positions_cache: List[Any] = []
        self._last_update_time: Optional[datetime] = None
    
    def list_positions(
        self, 
        account: Optional[Any] = None,
        unit: str = 'Common',
        timeout: int = 5000
    ) -> List[Any]:
        """列出持倉資訊
        
        取得指定帳戶的所有持倉，包括未實現損益。
        
        Args:
            account (Optional[Any]): 帳戶物件，None 表示使用預設股票帳戶
            unit (str): 單位類型，'Common'（整股）或其他，預設為 'Common'
            timeout (int): 逾時時間（毫秒），預設為 5000 毫秒（5 秒）
        
        Returns:
            List[Any]: Position 物件列表，包含 code, quantity, price, pnl 等資訊
        
        Examples:
            >>> from login import Login
            >>> login_service = Login()
            >>> api = login_service.login(api_key="...", secret_key="...")
            >>> account_mgr = AccountManager(api)
            >>> positions = account_mgr.list_positions()
            >>> for pos in positions:
            ...     print(f"{pos.code}: 數量={pos.quantity}, 未實現損益={pos.pnl}")
        
        Raises:
            RuntimeError: 當尚未設定股票帳戶且未提供 account 參數時
            ValueError: 當 unit 不在允許的值中時
            ValueError: 當 timeout 小於等於 0 時
            ConnectionError: 當無法連線到永豐 API 伺服器時
        """
        if account is None:
            if not hasattr(self._api, 'stock_account') or self._api.stock_account is None:
                raise RuntimeError("尚未設定股票帳戶，請先登入並確認帳戶設定")
            account = self._api.stock_account
        
        if unit not in ['Common', 'Share']:
            raise ValueError(f"Unit 必須是 'Common' 或 'Share'，當前值: {unit}")
        
        if timeout <= 0:
            raise ValueError(f"Timeout 必須大於 0，當前值: {timeout}")
        
        try:
            # 轉換單位類型
            unit_const = sj.constant.Unit.Common if unit == 'Common' else sj.constant.Unit.Share
            
            # 查詢持倉
            positions = self._api.list_positions(
                account=account,
                unit=unit_const,
                timeout=timeout
            )
            
            # 更新快取
            self._positions_cache = positions
            self._last_update_time = datetime.now()
            
            return positions
            
        except ConnectionError as e:
            raise ConnectionError(f"無法連線到永豐 API 伺服器: {e}")
        except OSError as e:
            raise ConnectionError(f"網路連線錯誤: {e}")
        except AttributeError as e:
            raise ValueError(f"無效的帳戶物件: {e}")
    
    def get_position_by_code(self, code: str) -> Optional[Any]:
        """根據商品代碼取得持倉資訊
        
        Args:
            code (str): 商品代碼，例如 "2330"
        
        Returns:
            Optional[Any]: Position 物件，如果找不到則返回 None
        
        Examples:
            >>> account_mgr = AccountManager(api)
            >>> account_mgr.list_positions()
            >>> position = account_mgr.get_position_by_code("2330")
            >>> if position:
            ...     print(f"持有數量: {position.quantity}")
        
        Raises:
            ValueError: 當 code 為空字串時
        """
        if not code:
            raise ValueError("商品代碼不可為空")
        
        for position in self._positions_cache:
            if hasattr(position, 'code') and position.code == code:
                return position
        
        return None
    
    def get_total_unrealized_pnl(self) -> float:
        """取得總未實現損益
        
        Returns:
            float: 總未實現損益金額
        
        Examples:
            >>> account_mgr = AccountManager(api)
            >>> account_mgr.list_positions()
            >>> total_pnl = account_mgr.get_total_unrealized_pnl()
            >>> print(f"總未實現損益: {total_pnl}")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        total_pnl = 0.0
        
        for position in self._positions_cache:
            if hasattr(position, 'pnl') and position.pnl is not None:
                try:
                    total_pnl += float(position.pnl)
                except (ValueError, TypeError):
                    continue
        
        return total_pnl
    
    def get_positions_by_direction(self, direction: str) -> List[Any]:
        """根據方向取得持倉列表
        
        Args:
            direction (str): 持倉方向，'Buy'（買入/做多）或 'Sell'（賣出/做空）
        
        Returns:
            List[Any]: 符合條件的 Position 物件列表
        
        Examples:
            >>> account_mgr = AccountManager(api)
            >>> account_mgr.list_positions()
            >>> long_positions = account_mgr.get_positions_by_direction('Buy')
            >>> print(f"做多持倉數: {len(long_positions)}")
        
        Raises:
            ValueError: 當 direction 不是 'Buy' 或 'Sell' 時
        """
        if direction not in ['Buy', 'Sell']:
            raise ValueError(f"Direction 必須是 'Buy' 或 'Sell'，當前值: {direction}")
        
        filtered_positions = []
        
        for position in self._positions_cache:
            if hasattr(position, 'direction'):
                direction_str = str(position.direction)
                if direction in direction_str:
                    filtered_positions.append(position)
        
        return filtered_positions
    
    def get_positions_with_profit(self) -> List[Any]:
        """取得盈利的持倉
        
        Returns:
            List[Any]: 未實現損益為正的 Position 物件列表
        
        Examples:
            >>> account_mgr = AccountManager(api)
            >>> account_mgr.list_positions()
            >>> profit_positions = account_mgr.get_positions_with_profit()
            >>> print(f"盈利持倉數: {len(profit_positions)}")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        profit_positions = []
        
        for position in self._positions_cache:
            if hasattr(position, 'pnl') and position.pnl is not None:
                try:
                    if float(position.pnl) > 0:
                        profit_positions.append(position)
                except (ValueError, TypeError):
                    continue
        
        return profit_positions
    
    def get_positions_with_loss(self) -> List[Any]:
        """取得虧損的持倉
        
        Returns:
            List[Any]: 未實現損益為負的 Position 物件列表
        
        Examples:
            >>> account_mgr = AccountManager(api)
            >>> account_mgr.list_positions()
            >>> loss_positions = account_mgr.get_positions_with_loss()
            >>> print(f"虧損持倉數: {len(loss_positions)}")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        loss_positions = []
        
        for position in self._positions_cache:
            if hasattr(position, 'pnl') and position.pnl is not None:
                try:
                    if float(position.pnl) < 0:
                        loss_positions.append(position)
                except (ValueError, TypeError):
                    continue
        
        return loss_positions
    
    def get_position_summary(self) -> Dict[str, Any]:
        """取得持倉摘要
        
        Returns:
            Dict[str, Any]: 持倉摘要資訊，包含總數、總未實現損益等
        
        Examples:
            >>> account_mgr = AccountManager(api)
            >>> account_mgr.list_positions()
            >>> summary = account_mgr.get_position_summary()
            >>> print(f"總持倉數: {summary['total_positions']}")
            >>> print(f"總未實現損益: {summary['total_unrealized_pnl']}")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        summary = {
            'total_positions': len(self._positions_cache),
            'total_unrealized_pnl': self.get_total_unrealized_pnl(),
            'profit_positions_count': len(self.get_positions_with_profit()),
            'loss_positions_count': len(self.get_positions_with_loss()),
            'last_update_time': self._last_update_time
        }
        
        return summary
    
    def get_last_update_time(self) -> Optional[datetime]:
        """取得上次更新時間
        
        Returns:
            Optional[datetime]: 上次更新持倉的時間，如果尚未更新過則返回 None
        
        Examples:
            >>> account_mgr = AccountManager(api)
            >>> account_mgr.list_positions()
            >>> last_time = account_mgr.get_last_update_time()
            >>> print(f"上次更新: {last_time}")
        
        Raises:
            此方法不會拋出任何錯誤
        """
        return self._last_update_time
    
    def clear_cache(self) -> None:
        """清除持倉快取
        
        Examples:
            >>> account_mgr = AccountManager(api)
            >>> account_mgr.list_positions()
            >>> account_mgr.clear_cache()
        
        Raises:
            此方法不會拋出任何錯誤
        """
        self._positions_cache.clear()
        self._last_update_time = None
