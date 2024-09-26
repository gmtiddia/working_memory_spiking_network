
/*
*  nestml_b1d63cdc7e584825bb59df1f45b8114e_module.cpp
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
*  2024-09-25 09:25:30.843420
*/

// Include from NEST
#include "nest_extension_interface.h"

// include headers with your own stuff



#include "new_stp_synapse_nestml.h"


class nestml_b1d63cdc7e584825bb59df1f45b8114e_module : public nest::NESTExtensionInterface
{
  public:
    nestml_b1d63cdc7e584825bb59df1f45b8114e_module() {}
    ~nestml_b1d63cdc7e584825bb59df1f45b8114e_module() {}

    void initialize() override;
};

nestml_b1d63cdc7e584825bb59df1f45b8114e_module nestml_b1d63cdc7e584825bb59df1f45b8114e_module_LTX_module;

void nestml_b1d63cdc7e584825bb59df1f45b8114e_module::initialize()
{
    // register synapses
    nest::register_new_stp_synapse_nestml( "new_stp_synapse_nestml" );
}
