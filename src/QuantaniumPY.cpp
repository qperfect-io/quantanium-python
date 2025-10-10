// 
// 
//  Copyright © 2032-2024 QPerfect. All Rights Reserved.
// 
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
// 
    //  http://www.apache.org/licenses/LICENSE-2.0
// 
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.
// 
#include <quantanium/Quantanium.hpp>

/// circuit simulator
#include <quantanium/impl/circuit/Circuit.hpp>
#include <quantanium/impl/circuit/Simulator.hpp>

#include <quantanium/impl/gates/BaseOperation.hpp>
#include <quantanium/impl/state/StateVectors.hpp>

/// format
#include <fmt/format.h>
/// openqasm
#include <quantanium/qasm/qasm2/OpenQASMCircuit.hpp>
/// protobuf
#include <quantanium/proto/ProtoCircuit.hpp>
#include <quantanium/proto/ProtoResult.hpp>

// Python Wrapper
#include <pybind11/iostream.h>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

namespace py = pybind11;

namespace qua = quantanium;


PYBIND11_MODULE(_core, m) {
  m.doc() = "pybind11 wrapper for Quantanium";

  py::class_<qua::from_proto::BitVector>(m, "BitVector")
        .def(py::init<size_t>()) // Constructor with number of qubits
        .def(py::init<
           const std::string &>()) 
        .def("print", &qua::from_proto::BitVector::Print) 
        .def("__str__", [](const qua::from_proto::BitVector& bv) {
            std::stringstream ss;
            ss << bv;
            return ss.str();
        })
        .def("__repr__", [](const qua::from_proto::BitVector& bv) {
            std::stringstream ss;
            ss << "<BitVector: " << bv << ">";
            return ss.str();
        });     


  // Wrap std::complex for float and double
  py::class_<std::complex<float>>(m, "ComplexF32")
      .def(py::init<float, float>())
      .def("real", [](const std::complex<float> &c) { return c.real(); })
      .def("imag", [](const std::complex<float> &c) { return c.imag(); });

  py::class_<std::complex<double>>(m, "ComplexF64")
      .def(py::init<double, double>())
      .def("real", [](const std::complex<double> &c) { return c.real(); })
      .def("imag", [](const std::complex<double> &c) { return c.imag(); });
  // Wrap CuStateVec 
  py::class_<qua::StateVector<float, quantanium::CPU>>(m, "StateVectorF32_CPU")
        .def(py::init<>())
        .def(py::init<std::size_t>())
        .def("numqubits", &qua::StateVector<float, quantanium::CPU>::NumQubits)
        .def("zerostate", &qua::StateVector<float, quantanium::CPU>::SetInitialState);

    py::class_<qua::StateVector<double, quantanium::CPU>>(m, "StateVectorF64_CPU")
        .def(py::init<>())
        .def(py::init<std::size_t>())
        .def("numqubits", &qua::StateVector<double, quantanium::CPU>::NumQubits)
        .def("zerostate", &qua::StateVector<double, quantanium::CPU>::SetInitialState);

 /* py::class_<qua::Simulator<double>>(m, "SimulatorDouble")
      .def(py::init<qua::from_proto::Circuit>())
      .def(py::init<qua::from_proto::Circuit, uint64_t>())
      .def("simulate_circuit", &qua::Simulator<double>::SimulateCircuit)
      .def("get_result", &qua::Simulator<double>::GetResult)
      .def("sampling", &qua::Simulator<double>::Sampling)
      .def("get_sv", &qua::Simulator<double>::GetStateVector);
*/
    py::class_<qua::Simulator<double, qua::CPU>>(m, "SimulatorDoubleCPU")
        .def(py::init<qua::from_proto::Circuit>())
        .def(py::init<qua::from_proto::Circuit, uint64_t>())
        .def(py::init<
            qua::from_proto::Circuit,
            qua::StateVector<double, qua::CPU>,
            uint64_t>())
        .def("simulate_circuit", &qua::Simulator<double, qua::CPU>::SimulateCircuit)
        .def("get_result", &qua::Simulator<double, qua::CPU>::GetResult)
        .def("sampling", &qua::Simulator<double, qua::CPU>::Sampling)
        .def("get_sv", &qua::Simulator<double, qua::CPU>::GetStateVector);
/*    #ifdef QUANTANIUM_USE_CUDA
    py::class_<qua::Simulator<double, qua::GPU>>(m, "SimulatorDoubleGPU")
        .def(py::init<qua::from_proto::Circuit>())
        .def(py::init<qua::from_proto::Circuit, uint64_t>())
        .def(py::init<
            qua::from_proto::Circuit,
            qua::StateVector<double, qua::GPU>,
            uint64_t>())
        .def("simulate_circuit", &qua::Simulator<double, qua::GPU>::SimulateCircuit)
        .def("get_result", &qua::Simulator<double, qua::GPU>::GetResult)
        .def("sampling", &qua::Simulator<double, qua::GPU>::Sampling)
        .def("get_sv", &qua::Simulator<double, qua::GPU>::GetStateVector);
    #endif*/
  py::class_<qua::from_proto::Circuit>(m, "Circuit")
      .def(py::init<>())
      .def("numqubits", &qua::from_proto::Circuit::numqubits)
      .def("numbits", &qua::from_proto::Circuit::numbits);

  py::class_<qua::from_proto::QCSResults>(m, "QCSResults")
      .def(py::init<>())
      .def("print_result", &qua::from_proto::QCSResults::Print)
      .def("get_fidelity", &qua::from_proto::QCSResults::GetFidelities)
      .def("get_version", &qua::from_proto::QCSResults::GetVersion);

  py::class_<qua::ProtoParser>(m, "ProtoParser")
      .def(py::init<>())
      .def("save_proto", &qua::ProtoParser::SaveProto)
      .def("load_proto", &qua::ProtoParser::LoadProto);

  py::class_<qua::ProtoResult>(m, "ProtoResult")
      .def(py::init<>())
      .def("save_proto", &qua::ProtoResult::SaveProto)
      .def("load_proto", &qua::ProtoResult::LoadProto);
    m.def("execute_double_cpu",
        [](qua::from_proto::Circuit &circuit, int shots, int seed,
            std::vector<qua::from_proto::BitVector> &bitstrings) {
            // Explicitly define the tuple type
            quantanium::from_proto::QCSResults full_result =
                qua::Execute_ext<double>(circuit,
                                        static_cast<unsigned long>(shots),
                                        static_cast<unsigned long>(seed),
                                        bitstrings);

            // Extract values correctly
            quantanium::from_proto::QCSResults result = full_result;

            return result;
        });
// old version 
// TO DO -  return sv (as before) only for cpu !!!
  /*  m.def("execute_double_cpu",
      [](qua::from_proto::Circuit &circuit, int shots, int seed,
         std::vector<qua::from_proto::BitVector> &bitstrings) {
        // Explicitly define the tuple type
        std::tuple<quantanium::from_proto::QCSResults, std::vector<std::complex<double>>> full_result =
            qua::Execute_ext<double >(circuit,
                                     static_cast<unsigned long>(shots),
                                     static_cast<unsigned long>(seed),
                                     bitstrings);

        // Extract values correctly
        quantanium::from_proto::QCSResults result = std::get<0>(full_result);
        std::vector<std::complex<double>> sv = std::get<1>(full_result);

        return py::make_tuple(result, sv);
      });*/
        m.def("execute_double_cpu",
        [](qua::from_proto::Circuit& circuit,
            unsigned long              shots,
            unsigned long              seed,
            std::vector<qua::from_proto::BitVector>& bitstrings) {
            auto result = qua::Execute_ext<double, qua::CPU>(circuit, shots, seed, bitstrings);
            return result;
        },
        py::arg("circuit"),
        py::arg("shots"),
        py::arg("seed"),
        py::arg("bitstrings")
        );

#if QUANTANIUM_USE_CUDA
    m.def("execute_double_gpu",
        [](qua::from_proto::Circuit& circuit,
            unsigned long              shots,
            unsigned long              seed,
            std::vector<qua::from_proto::BitVector>& bitstrings) {
            auto result = qua::Execute_ext<double, qua::GPU>(circuit, shots, seed, bitstrings);
            return result;
        },
        py::arg("circuit"),
        py::arg("shots"),
        py::arg("seed"),
        py::arg("bitstrings")
        );
#endif
    m.def("evolve",
    [](
        qua::from_proto::Circuit& circuit,
        unsigned long              seed,
        bool stop_before_measure) {
        return qua::Evolve<double>(circuit, seed, stop_before_measure);  
    },
    py::arg("circuit"),
    py::arg("seed"),
    py::arg("stop_before_measure") = false);

    m.def("evolve_next",
    []( qua::StateVector<double>& sv,
        qua::from_proto::Circuit& circuit,
        unsigned long              seed,
        bool stop_before_measure) {
        return qua::Evolve_next<double>(sv, circuit, seed, stop_before_measure);  
    },
    py::arg("sv"),
    py::arg("circuit"),
    py::arg("seed"),
    py::arg("stop_before_measure") = false);
      
  m.def("load_open_qasm", &qua::LoadOpenQASM);

  py::class_<qua::BaseOperationStrategy<double, 1>>(
      m, "BaseOperationStrategyDouble")
      .def("apply", &qua::BaseOperationStrategy<double, 1>::Apply);

  py::class_<qua::Gate1Q<double>, qua::BaseOperationStrategy<double, 1>>(
      m, "Gate1QDouble")
      .def("apply", &qua::Gate1Q<double>::Apply);

  py::class_<qua::GateX<double>, qua::Gate1Q<double>>(m, "GateXDouble")
      .def("apply", &qua::GateX<double>::Apply);
}



