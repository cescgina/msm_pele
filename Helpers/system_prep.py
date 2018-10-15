import os
import subprocess
import argparse
import MSM_PELE.Helpers.pele_env as pl
import MSM_PELE.constants as cs

class SystemBuilder(pl.EnviroBuilder):
    def __init__(self, receptor, ligand, residue, pele_dir):
        self.receptor = receptor
        self.ligand = ligand
        self.residue = residue
        self.pele_dir = pele_dir
        self.system = None if self.ligand else self.receptor

    @classmethod
    def build_system(cls, receptor, ligand, residue, pele_dir, output=False):
        SPYTHON = os.path.join(cs.SCHRODINGER, "utilities/python")
        if ligand:
            system = cls(receptor, ligand, residue, pele_dir)
            system.lig_ref = os.path.join(pele_dir, "ligand.pdb")
            subprocess.call("{} {} {} {} --mae".format(SPYTHON, __file__, system.ligand, system.lig_ref).split())
            system.system = system.build_complex()
        else:
            system = cls(receptor, ligand, residue, pele_dir)
            system.receptor, system.lig_ref = system.retrieve_receptor(output=output)
            subprocess.call("{} {} {} {}".format(SPYTHON, __file__, system.lig_ref, pele_dir).split())
            system.lig = "{}.mae".format(residue)
            system.residue = residue
        return system

    def build_complex(self):
        """
            From the receptor and ligand in pdb build
            another pdb with the whole complex
        """
        complex_content = []

        name = os.path.basename(os.path.splitext(self.receptor)[0])
        self.complex = os.path.join(self.pele_dir, "{}_complex.pdb".format(name))

        with open(self.receptor, 'r') as pdb_file:
            receptor_text = [line for line in pdb_file if line.startswith("ATOM") or line.startswith("HETATM") or line.startswith("TER")]
        with open(self.lig_ref, 'r') as pdb_file:
            ligand_text = [line for line in pdb_file if line.startswith("HETATM")]
        if not receptor_text  or not ligand_text:
            raise ValueError("The ligand_pdb was not properly created check your mae file")

        complex_content.extend(receptor_text + ["TER\n"] + ligand_text + ["END"])

        with open(self.complex, 'w') as fout:
            fout.write("".join(complex_content))

        return self.complex

    def convert_mae(self):
        """
           Desciption: From each structure retrieve
           a .mae file of the ligand in the receptor.

           Output:
                structure_mae: ligand
                res = residue
        """

        for structure in st.StructureReader(self.lig_ref):
            for residue in structure.residue:
                res = residue.pdbres.strip()
            str_name = "{}".format(res)
            try:
                structure.write(str_name + ".mae")
            except ValueError:
                str_name = "{}".format(res)
            finally:
                structure.write(str_name + ".mae")
                structure_mae = "{}.mae".format(str_name)
        return structure_mae, res

    def retrieve_receptor(self, output=False):
        """
        This function returns receptor of the complex of interest.

        :param complex: system format pdb

        :output: receptor text
        """
        ligand = output if output else os.path.join(self.pele_dir, "ligand.pdb")    

        with open(self.receptor, 'r') as pdb_file:
            receptor_text = [line for line in pdb_file if line.startswith("ATOM")]
        with open(self.receptor, 'r') as pdb_file:
            ligand_text = [line for line in pdb_file if line[17:20].strip() == self.residue]
        if not receptor_text  or not ligand_text:
            raise ValueError("Something went wrong when extracting the ligand. Check residue&Chain on input")
        with open(ligand, "w") as fout:
            fout.write("".join(ligand_text))

        return "".join(receptor_text), ligand

def convert_pdb(mae_file, output_dir):
    from schrodinger import structure as st
    for structure in st.StructureReader(mae_file):
        structure.write(output_dir)


def convert_mae(pdb):
    """
        Desciption: From each structure retrieve
        a .mae file of the ligand in the receptor.
        Output:
             structure_mae: ligand
             res = residue
    """
    from schrodinger import structure as st
    for structure in st.StructureReader(pdb):
        for residue in structure.residue:
            res = residue.pdbres.strip()
            str_name = "{}".format(res)
            try:
                structure.write(str_name + ".mae")
            except ValueError:
                str_name = "{}".format(res)
            finally:
                structure.write(str_name + ".mae")
                structure_mae = "{}.mae".format(str_name)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("ligand", help="ligand input file to convert")
    parser.add_argument("output_dir", help="output directory to dump the converted file")
    parser.add_argument("--mae", action="store_true", help="Whether to convert to mae (--mae) or pdb (not --mae)")
    args = parser.parse_args()
    return args.ligand, args.output_dir, args.mae




if __name__ == "__main__":
    input_file, output_dir, ligand_mae = parse_args()
    if ligand_mae:
        convert_pdb(input_file, output_dir)
    else:
        convert_mae(input_file)
        

