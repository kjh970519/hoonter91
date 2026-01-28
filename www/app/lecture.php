<?php

//
// Controller for display
// https://{domain}/lecture/career
//
class Career extends \controller\Make_Controller {

    public function init()
    {
        $this->layout()->category_key(31);
        $this->layout()->head();
        $this->layout()->view();
        $this->layout()->foot();
    }

    public function make(){
        $this->module();
    }

    public function module(){
        $module = new \Module\Board\Make_Controller();
        $module->set('id', 'lecture_career');
        $module->run();
    }

}
