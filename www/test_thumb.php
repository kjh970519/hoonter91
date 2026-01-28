<?php
chdir('/var/www/html');
require_once '/var/www/html/inc/core.php';

$sql = new \Make\Database\Pdosql();
$sql->query("SELECT idx, subject, article, file1, file2 FROM zg_mod_board_data_story_album LIMIT 1", []);
$arr = $sql->fetchs();

echo "idx: " . $arr['idx'] . "\n";
echo "subject: " . $arr['subject'] . "\n";
echo "file1: " . ($arr['file1'] ?: 'empty') . "\n";
echo "file2: " . ($arr['file2'] ?: 'empty') . "\n";
echo "article length: " . strlen($arr['article']) . "\n";

// test regex
preg_match('/<img[^>]+src=["\']([^"\']+)["\']/', $arr['article'], $matches);
echo "regex match: " . (!empty($matches[1]) ? $matches[1] : 'no match') . "\n";
