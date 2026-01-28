<?php
namespace Module\Message;

use Corelib\Func;
use Make\Database\Pdosql;

//
// Module : Message Library
//

class Library {

    // 모듈 초기화
    public function __construct()
    {
        $sql = new Pdosql();
    }

    // 새로운 메시지 카운팅
    public function get_new_count()
    { 
        $sql = new Pdosql();

        $total_count = 0;
        if (IS_MEMBER) {
            $sql->query(
                "
                select count(*) as total
                from {$sql->table("mod:message")} a
                where `to_mb_idx`=:col1 and a.`msg_type`=:col2 and `chked` is null and `dregdate` is null
                ",
                array(
                    MB_IDX, 'received'
                )
            );
            $total_count = $sql->fetch('total');

        }

        return $total_count;

    }

}
