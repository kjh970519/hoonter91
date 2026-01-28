<?php

//
// Controller for display
// https://{domain}/jinyong/free
//
class Free extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(39);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make(){
        $this->module();
    }

    public function module(){
        $module = new \Module\Board\Make_Controller();
        $module->set('id', 'jinyong_free');
        $module->run();
    }

}
