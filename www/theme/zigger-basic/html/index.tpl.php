<?php
// 팝업 출력
$this->popup_fetch();
?>

<div class="lat-wrap">

    <div class="lat">
        <a href="<?php echo PH_DIR; ?>/community/notice" class="more"><i class="fa fa-plus"></i><p>더보기</p></a>
        <?php
        // 공지사항 최근게시물
        $this->latest_notice();
        ?>
    </div>

    <div class="lat">
        <a href="<?php echo PH_DIR; ?>/story/album" class="more"><i class="fa fa-plus"></i><p>더보기</p></a>
        <?php
        // 행복한이야기 최근게시물
        $this->latest_story();
        ?>
    </div>

</div>
