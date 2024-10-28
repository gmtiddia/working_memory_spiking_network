
/*
*  nestml_135112b452334dcd851726f8bc861a61_module.cpp
*
*  This file is part of NEST.
*
*  Copyright (C) 2004 The NEST Initiative
*
*  NEST is free software: you can redistribute it and/or modify
*  it under the terms of the GNU General Public License as published by
*  the Free Software Foundation, either version 2 of the License, or
*  (at your option) any later version.
*
*  NEST is distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*  GNU General Public License for more details.
*
*  You should have received a copy of the GNU General Public License
*  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
*
*  2024-10-22 11:51:12.675573
*/

// Include from NEST
#include "nest_extension_interface.h"

// include headers with your own stuff



#include "stp_synapse_nestml.h"


class nestml_135112b452334dcd851726f8bc861a61_module : public nest::NESTExtensionInterface
{
  public:
    nestml_135112b452334dcd851726f8bc861a61_module() {}
    ~nestml_135112b452334dcd851726f8bc861a61_module() {}

    void initialize() override;
};

nestml_135112b452334dcd851726f8bc861a61_module nestml_135112b452334dcd851726f8bc861a61_module_LTX_module;

void nestml_135112b452334dcd851726f8bc861a61_module::initialize()
{
    // register synapses
    nest::register_stp_synapse_nestml( "stp_synapse_nestml" );
}
