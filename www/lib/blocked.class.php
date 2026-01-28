<?php
namespace Corelib;

use Corelib\Func;
use Make\Database\Pdosql;

class Blocked {

    static public function get_qry()
    {
        $ip_ex = explode('.', MB_REMOTE_ADDR);
        $ip_qry = [];
        $ip_qry_var = [];

        // 모든 조합을 만들기 위한 반복문
        for ($i = 0; $i < 16; $i++) { // 2^4 = 16 (각 자리마다 * 포함 여부)
            $pattern = [];

            for ($j = 0; $j < 4; $j++) {
                if ($i & (1 << $j)) {
                    $pattern[] = '*';
                } else {
                    $pattern[] = $ip_ex[$j];
                }
            }

            $ip_qry[] = implode('.', $pattern);
        }

        foreach ($ip_qry as $key => $value) {
            $ip_qry_var['qry'][] = '`ip`=:ip_col'.($key + 1);
            $ip_qry_var['cols']['ip_col'.($key + 1)] = $value;
        }
        $ip_qry_var['qry'] = implode(' or ', $ip_qry_var['qry']);

        return $ip_qry_var;
    }

    static public function chk_block()
    {
        global $MB;

        $localhosts = array('127.0.0.1', '::1', 'localhost', '255.255.255.0');

        if (in_array(MB_REMOTE_ADDR, $localhosts)) return false;

        $sql = new Pdosql();

        $qry = self::get_qry();
        $qry_cols = array_merge(
            $qry['cols'],
            [
                'mb_idx' => $MB['idx'],
                'mb_id' => $MB['id']
            ]
        );

        $sql->query(
            "
            select *
            from {$sql->table("blockmb")}
            where ({$qry['qry']}) or (`mb_idx`=:mb_idx and `mb_id`=:mb_id)
            ",
            $qry_cols
        );

        $uri = Func::thisuri();
        $loc_page = PH_DIR.'/member/warning';

        if ($sql->getcount() > 0 && $uri != $loc_page) Func::location($loc_page);

    }
}

Blocked::chk_block();
