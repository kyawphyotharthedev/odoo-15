from odoo import models, fields

BOARD_USER_LIST = [
    'ideatime_core.ideatime_user_kyawmyohlaing',
    'ideatime_core.ideatime_user_yinwinaye'
]


class IdeatimeBoardGroup(models.AbstractModel):
    _name = "ideatime.board.group"
    _description = "IdeaTime Board Group"

    allowed_user_ids = fields.Many2many('res.users', string='Allowed Users')

    def _get_board_users(self):
        board_users = self.env['res.users']
        for board in BOARD_USER_LIST:
            board_users |= self.env.ref(board)
        return board_users

    def _add_board_users_to_allowed_uids(self):
        for record in self:
            board_users = self._get_board_users()
            for line in board_users:
                if line in record.allowed_user_ids:
                    continue
                record.allowed_user_ids|=line
