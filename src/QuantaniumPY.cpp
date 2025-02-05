//===-- QuantaniumPY.cpp ---------------------------------------*- C++ -*-===//
//
//                            Quantanium by MIMIQ
//
// Copyright (C) 2023-2024 QPerfect. All Rights Reserved.
// Unauthorized copying of this file, via any medium is strictly prohibited.
// Proprietary and confidential.
//
//===---------------------------------------------------------------------===//
///
/// @file
/// @brief      Python wrappers
///
//===---------------------------------------------------------------------===//
// quantanium
#include <quantanium/Quantanium.hpp>

/// circuit simulator
#include <quantanium/impl/circuit/Circuit.hpp>
#include <quantanium/impl/circuit/Simulator.hpp>

#include <quantanium/impl/gates/BaseOperation.hpp>
#include <quantanium/impl/state/StateVector.hpp>
#include <quantanium/utils/SignalHandler.hpp>
// #include <quantanium/impl/state/State.hpp>
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
// namespace quantanium {

PYBIND11_MODULE(_core, m) {
  m.doc() = "pybind11 wrapper for Quantanium";

  py::class_<qua::from_proto::BitVector>(m, "BitVector")
      .def(py::init<size_t>()) // Constructor with number of qubits
      .def(py::init<
           const std::string &>()); // Constructor with binary string
                                    // .def_static("fromint",
                                    // &qua::from_proto::BitString::fromint,
  //             py::arg("num_qubits"), py::arg("value"), py::arg("endian") =
  //             "big")

  // Wrap std::complex for float and double
  py::class_<std::complex<float>>(m, "ComplexF32")
      .def(py::init<float, float>())
      .def("real", [](const std::complex<float> &c) { return c.real(); })
      .def("imag", [](const std::complex<float> &c) { return c.imag(); });

  py::class_<std::complex<double>>(m, "ComplexF64")
      .def(py::init<double, double>())
      .def("real", [](const std::complex<double> &c) { return c.real(); })
      .def("imag", [](const std::complex<double> &c) { return c.imag(); });

  // Wrap StateVector
  py::class_<qua::StateVector<float>>(m, "StateVectorF32")
      .def(py::init<>())
      .def(py::init<std::size_t>())
      .def("get_size", &qua::StateVector<float>::GetSize)
      .def("numqubits", &qua::StateVector<float>::NumQubits)
      .def("zerostate", &qua::StateVector<float>::SetInitialState)
      .def("get_real", &qua::StateVector<float>::GetReal)
      .def("get_imag", &qua::StateVector<float>::GetImag);

  py::class_<qua::StateVector<double>>(m, "StateVectorF64")
      .def(py::init<>())
      .def(py::init<std::size_t>())
      .def("get_size", &qua::StateVector<double>::GetSize)
      .def("numqubits", &qua::StateVector<double>::NumQubits)
      .def("zerostate", &qua::StateVector<double>::SetInitialState)
      .def("get_real", &qua::StateVector<double>::GetReal)
      .def("get_imag", &qua::StateVector<double>::GetImag);

  py::class_<qua::Simulator<double>>(m, "SimulatorDouble")
      .def(py::init<qua::from_proto::Circuit>())
      .def(py::init<qua::from_proto::Circuit, uint64_t>())
      .def("simulate_circuit", &qua::Simulator<double>::SimulateCircuit)
      .def("get_result", &qua::Simulator<double>::GetResult)
      .def("sampling", &qua::Simulator<double>::Sampling)
      .def("get_sv", &qua::Simulator<double>::GetStateVector);

  py::class_<qua::from_proto::Circuit>(m, "Circuit")
      .def(py::init<>())
      .def("numqubits", &qua::from_proto::Circuit::numqubits)
      .def("numbits", &qua::from_proto::Circuit::numbits);

  py::class_<qua::from_proto::QCSResults>(m, "QCSResults")
      .def(py::init<>())
      .def("print_result", &qua::from_proto::QCSResults::Print)
      //  .def("get_cstate", &qua::from_proto::QCSResults::GetCState)
      //  .def("get_cstates_str", &qua::from_proto::QCSResults::GetCStatesStr)
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

  // Wrapper for execute function
  // m.def("execute_float", &qua::Execute<float>);
  // m.def("execute_double", &qua::Execute_ext<double>);
/*  m.def("execute_double",
        [](qua::from_proto::Circuit &circuit, int shots, int seed,
           std::vector<qua::from_proto::BitVector> &bitstrings) {
          return qua::Execute_ext<double>(
              circuit, static_cast<unsigned long>(shots),
              static_cast<unsigned long>(seed), bitstrings);
        });
*/
/*  m.def("execute_double",
      [](qua::from_proto::Circuit &circuit, int shots, int seed,
         std::vector<qua::from_proto::BitVector> &bitstrings) {
        auto [result, sv] = qua::Execute_ext<double>(
            circuit, static_cast<unsigned long>(shots),
            static_cast<unsigned long>(seed), bitstrings);
        return py::make_tuple(result, sv);
      });
*/
    m.def("execute_double",
      [](qua::from_proto::Circuit &circuit, int shots, int seed,
         std::vector<qua::from_proto::BitVector> &bitstrings) {
        // Explicitly define the tuple type
        std::tuple<quantanium::from_proto::QCSResults, std::vector<std::complex<double>>> full_result =
            qua::Execute_ext<double>(circuit,
                                     static_cast<unsigned long>(shots),
                                     static_cast<unsigned long>(seed),
                                     bitstrings);

        // Extract values correctly
        quantanium::from_proto::QCSResults result = std::get<0>(full_result);
        std::vector<std::complex<double>> sv = std::get<1>(full_result);

        return py::make_tuple(result, sv);
      });
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

//} // namespace quantanium

// vim: set ft=cpp ts=2 sts=2 et sw=2 tw=80: //
